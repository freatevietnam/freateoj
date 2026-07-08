# coding=utf-8
import logging
import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import get_default_password_validators
from django.core.mail import send_mail
from django.db import transaction
from django.forms import ChoiceField, ModelChoiceField
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext, gettext_lazy as _, ngettext
from django.views import View
from django.views.generic import TemplateView
from registration.forms import RegistrationForm
from sortedm2m.forms import SortedMultipleChoiceField

from judge.forms import SocialAuthMixin
from judge.models import Language, Organization, Profile, TIMEZONE
from judge.models.email_verification import EmailVerification
from judge.utils.recaptcha import ReCaptchaField, ReCaptchaWidget
from judge.utils.subscription import Subscription, newsletter_id
from judge.widgets import Select2MultipleWidget, Select2Widget

bad_mail_regex = list(map(re.compile, settings.BAD_MAIL_PROVIDER_REGEX))
logger = logging.getLogger(__name__)


class CustomRegistrationForm(RegistrationForm):
    username = forms.RegexField(regex=re.compile(r'^\w+$', re.ASCII), max_length=30, label=_('Username'),
                                error_messages={'invalid': _('A username must contain letters, '
                                                             'numbers, or underscores.')})
    full_name = forms.CharField(max_length=30, label=_('Full name'), required=False)
    timezone = ChoiceField(label=_('Timezone'), choices=TIMEZONE,
                           widget=Select2Widget(attrs={'style': 'width:100%'}))
    language = ModelChoiceField(queryset=Language.objects.all(), label=_('Preferred language'), empty_label=None,
                                widget=Select2Widget(attrs={'style': 'width:100%'}))
    organizations = SortedMultipleChoiceField(queryset=Organization.objects.filter(is_open=True),
                                              label=_('Organizations'), required=False,
                                              widget=Select2MultipleWidget(attrs={'style': 'width:100%'}))

    if newsletter_id is not None:
        newsletter = forms.BooleanField(label=_('Subscribe to newsletter?'), initial=True, required=False)

    if ReCaptchaField is not None:
        captcha = ReCaptchaField(widget=ReCaptchaWidget())

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(gettext('The email address "%s" is already taken. Only one registration '
                                                'is allowed per address.') % self.cleaned_data['email'])
        if '@' in self.cleaned_data['email']:
            domain = self.cleaned_data['email'].split('@')[-1].lower()
            if (domain in settings.BAD_MAIL_PROVIDERS or
                    any(regex.match(domain) for regex in bad_mail_regex)):
                raise forms.ValidationError(gettext('Your email provider is not allowed due to history of abuse. '
                                                    'Please use a reputable email provider.'))
        return self.cleaned_data['email']

    def clean_organizations(self):
        organizations = self.cleaned_data.get('organizations') or []
        max_orgs = settings.DMOJ_USER_MAX_ORGANIZATION_COUNT
        if len(organizations) > max_orgs:
            raise forms.ValidationError(ngettext('You may not be part of more than {count} public organization.',
                                                 'You may not be part of more than {count} public organizations.',
                                                 max_orgs).format(count=max_orgs))
        return self.cleaned_data['organizations']


class RegistrationView(View):
    title = _('Register')
    form_class = CustomRegistrationForm
    social_auth = SocialAuthMixin()
    template_name = 'registration/registration_form.html'
    http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        kwargs['TIMEZONE_MAP'] = settings.TIMEZONE_MAP
        kwargs['password_validators'] = get_default_password_validators()
        kwargs['tos_url'] = settings.TERMS_OF_SERVICE_URL
        kwargs['oauth_only'] = settings.OAUTH_ONLY
        kwargs['oauth'] = self.social_auth
        return kwargs

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial={
            'timezone': settings.DEFAULT_USER_TIME_ZONE,
            'language': Language.objects.get(key=settings.DEFAULT_USER_LANGUAGE),
        })
        context = self.get_context_data(form=form, **kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            context = self.get_context_data(form=form, **kwargs)
            return render(request, self.template_name, context)
        return self.register(form)

    def _send_verification_email(self, user, verification):
        email_verification_enabled = getattr(settings, 'EMAIL_VERIFICATION_ENABLED', True)
        if not email_verification_enabled:
            return True

        site_name = getattr(settings, 'SITE_NAME', 'FreateOJ')
        site_domain = getattr(settings, 'DMOJ_CANONICAL', 'oj.freate.io.vn')
        subject = gettext('Verify your %(site_name)s email address') % {'site_name': site_name}
        message = render_to_string('registration/verification_email.txt', {
            'user': user,
            'otp_code': verification.otp_code,
            'expires_minutes': getattr(settings, 'EMAIL_VERIFICATION_EXPIRY_MINUTES', 60),
            'site_name': site_name,
            'site_domain': site_domain,
        })
        html_message = render_to_string('registration/verification_email.html', {
            'user': user,
            'otp_code': verification.otp_code,
            'expires_minutes': getattr(settings, 'EMAIL_VERIFICATION_EXPIRY_MINUTES', 60),
            'site_name': site_name,
            'site_domain': site_domain,
        })

        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@freate.io.vn')
            from_name = getattr(settings, 'DEFAULT_FROM_NAME', '')
            if from_email and from_name:
                from_email = '%s <%s>' % (from_name, from_email)

            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error('Failed to send verification email to %s: %s', user.email, str(e))
            return False

    @transaction.atomic
    def register(self, form):
        email_verification_enabled = getattr(settings, 'EMAIL_VERIFICATION_ENABLED', True)

        cleaned_data = form.cleaned_data
        user = User.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            password=cleaned_data['password1'],
        )

        if email_verification_enabled:
            user.is_active = False
            user.save(update_fields=['is_active'])

        profile, __ = Profile.objects.get_or_create(user=user, defaults={
            'language': Language.get_default_language(),
        })

        user.first_name = cleaned_data['full_name']
        profile.timezone = cleaned_data['timezone']
        profile.language = cleaned_data['language']
        profile.organizations.add(*cleaned_data['organizations'])

        user.save()
        profile.save()

        if newsletter_id is not None and cleaned_data.get('newsletter'):
            Subscription(user=user, newsletter_id=newsletter_id, subscribed=True).save()

        if email_verification_enabled:
            verification = EmailVerification.create_for_user(user)
            email_sent = self._send_verification_email(user, verification)
            if not email_sent:
                return render(self.request, 'registration/email_send_error.html', {
                    'title': _('Email Verification Error'),
                }, status=500)

        self.request.session['completed_username'] = user.username

        return redirect(self.get_success_url(user))

    def get_success_url(self, user=None):
        if user and getattr(settings, 'EMAIL_VERIFICATION_ENABLED', True):
            return '/accounts/verify/%s/' % user.username
        return '/accounts/register/complete/'



class OTPVerificationView(TemplateView):
    title = _('Verify Email')
    template_name = 'registration/verify_otp.html'
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'otp_error' in request.session:
            context['error'] = request.session.pop('otp_error')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        otp_code = request.POST.get('otp_code', '').strip().upper()
        username = kwargs.get('username', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            request.session['otp_error'] = _('Invalid verification request.')
            return redirect('registration_verify_otp', username=username)

        try:
            verification = EmailVerification.objects.get(user=user, is_verified=False)
        except EmailVerification.DoesNotExist:
            request.session['otp_error'] = _('No pending verification found. Please register again.')
            return redirect('registration_verify_otp', username=username)

        success, message = verification.verify(otp_code)
        if success:
            user.is_active = True
            user.save(update_fields=['is_active'])
            return redirect('registration_activation_complete')
        else:
            request.session['otp_error'] = message
            return redirect('registration_verify_otp', username=username)

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        kwargs['username'] = self.kwargs.get('username', '')
        return super().get_context_data(**kwargs)


class ResendVerificationView(TemplateView):
    title = _('Resend Verification Email')
    template_name = 'registration/resend_verification.html'
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'registration/resend_verification.html', {
                'title': _('Resend Verification Email'),
                'error': _('User not found.'),
                'username': username,
            })

        if user.is_active:
            return render(request, 'registration/resend_verification.html', {
                'title': _('Resend Verification Email'),
                'error': _('This account is already verified.'),
                'username': username,
            })

        verification = EmailVerification.create_for_user(user)

        site_name = getattr(settings, 'SITE_NAME', 'FreateOJ')
        site_domain = getattr(settings, 'DMOJ_CANONICAL', 'oj.freate.io.vn')
        subject = gettext('Verify your %(site_name)s email address') % {'site_name': site_name}
        message = render_to_string('registration/verification_email.txt', {
            'user': user,
            'otp_code': verification.otp_code,
            'expires_minutes': getattr(settings, 'EMAIL_VERIFICATION_EXPIRY_MINUTES', 60),
            'site_name': site_name,
            'site_domain': site_domain,
        })
        html_message = render_to_string('registration/verification_email.html', {
            'user': user,
            'otp_code': verification.otp_code,
            'expires_minutes': getattr(settings, 'EMAIL_VERIFICATION_EXPIRY_MINUTES', 60),
            'site_name': site_name,
            'site_domain': site_domain,
        })

        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@freate.io.vn')
            from_name = getattr(settings, 'DEFAULT_FROM_NAME', '')
            if from_email and from_name:
                from_email = '%s <%s>' % (from_name, from_email)

            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return redirect('/accounts/verify/%s/' % username)
        except Exception as e:
            logger.error('Failed to resend verification email to %s: %s', user.email, str(e))
            return render(request, 'registration/resend_verification.html', {
                'title': _('Resend Verification Email'),
                'error': _('Failed to send verification email. Please contact the administrator to verify your account.'),
                'username': username,
            })

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        kwargs['username'] = self.kwargs.get('username', '')
        return super().get_context_data(**kwargs)


def social_auth_error(request):
    return render(request, 'generic-message.html', {
        'title': gettext('Authentication failure'),
        'message': request.GET.get('message'),
    })


class RegistrationCompleteView(TemplateView):
    title = _('Registration Completed')
    template_name = 'registration/registration_complete.html'

    def get(self, request, *args, **kwargs):
        email_verification_enabled = getattr(settings, 'EMAIL_VERIFICATION_ENABLED', True)
        completed_username = request.session.get('completed_username', '')
        context = self.get_context_data(**kwargs)
        context['email_verification_enabled'] = email_verification_enabled
        context['completed_username'] = completed_username
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        return super().get_context_data(**kwargs)
