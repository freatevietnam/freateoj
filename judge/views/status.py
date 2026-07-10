from collections import defaultdict
from functools import partial

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from packaging import version

from judge.models import Judge, Language, RuntimeVersion


def get_judges(request):
    if request.user.is_superuser or request.user.is_staff:
        return True, Judge.objects.order_by('-online', 'name')
    else:
        return False, Judge.objects.filter(online=True)


def status_all(request):
    see_all, judges = get_judges(request)
    languages = Language.objects.filter(runtimeversion__isnull=False).distinct().order_by('key')
    
    return render(request, 'status/status.html', {
        'judges': judges,
        'runtime_version_data': Judge.runtime_versions(),
        'see_all_judges': see_all,
        'languages': languages,
    })


def status_table(request):
    see_all, judges = get_judges(request)
    html = render_to_string('status/judge-status-table.html', {
        'judges': judges,
        'runtime_version_data': Judge.runtime_versions(),
        'see_all_judges': see_all,
    })
    return HttpResponse(html)
