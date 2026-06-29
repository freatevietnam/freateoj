import secrets
import string

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_verification')
    otp_code = models.CharField(max_length=8, verbose_name=_('OTP Code'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    expires_at = models.DateTimeField(verbose_name=_('Expires at'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Is verified'))
    attempts = models.IntegerField(default=0, verbose_name=_('Attempts'))

    class Meta:
        verbose_name = _('Email Verification')
        verbose_name_plural = _('Email Verifications')

    def __str__(self):
        return f'{self.user.username} - {self.otp_code}'

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=60)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_otp():
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(8))

    def is_expired(self):
        return timezone.now() > self.expires_at

    def verify(self, code):
        if self.is_expired():
            return False, _('Verification code has expired. Please request a new one.')
        if self.is_verified:
            return False, _('This verification code has already been used.')
        if self.attempts >= 5:
            return False, _('Too many failed attempts. Please request a new verification code.')
        self.attempts += 1
        self.save(update_fields=['attempts'])
        if self.otp_code != code.upper():
            return False, _('Invalid verification code. You have %(remaining)d attempts remaining.') % {
                'remaining': 5 - self.attempts
            }
        self.is_verified = True
        self.save(update_fields=['is_verified'])
        return True, _('Verification successful!')

    @classmethod
    def create_for_user(cls, user):
        # Delete any existing verification for this user
        cls.objects.filter(user=user).delete()
        otp_code = cls.generate_otp()
        verification = cls.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=60),
        )
        return verification
