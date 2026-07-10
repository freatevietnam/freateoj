from collections import defaultdict
from functools import partial

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.utils.translation import gettext as _
from packaging import version

from judge.models import Judge, Language, RuntimeVersion

__all__ = ['status_all', 'status_table']


def get_judges(request):
    if request.user.is_superuser or request.user.is_staff:
        return True, Judge.objects.order_by('-online', 'name')
    else:
        return False, Judge.objects.filter(online=True)


def status_all(request):
    """Combined status page with judges, runtimes, and version matrix."""
    see_all, judges = get_judges(request)
    
    # Get languages for runtimes tab
    languages = Language.objects.filter(judges__online=True).distinct().order_by('key')
    
    # Get version matrix data
    matrix = defaultdict(partial(defaultdict, LatestList))
    latest = defaultdict(list)
    groups = defaultdict(list)

    judge_ids = {judge.id: judge.name for judge in Judge.objects.filter(online=True)}
    
    for runtime in RuntimeVersion.objects.filter(judge__online=True).order_by('priority'):
        matrix[runtime.judge_id][runtime.language_id].append(runtime)

    for judge_id, data in matrix.items():
        name_tuple = judge_ids[judge_id].rpartition('.')
        groups[name_tuple[0] or name_tuple[-1]].append((judge_ids[judge_id], data))

    matrix_data = {}
    for group, data in groups.items():
        if len(data) == 1:
            judge_name, data = data[0]
            matrix_data[judge_name] = data
            continue

        ds = list(range(len(data)))
        size = [1] * len(data)
        for i, (p, x) in enumerate(data):
            if ds[i] != i:
                continue
            for j, (q, y) in enumerate(data):
                if i != j and compare_version_list(x, y):
                    ds[j] = i
                    size[i] += 1
                    size[j] = 0

        rep = max(range(len(data)), key=size.__getitem__)
        matrix_data[group] = data[rep][1]
        for i, (j, x) in enumerate(data):
            if ds[i] != rep:
                matrix_data[j] = x

    for data in matrix_data.values():
        for language, versions in data.items():
            versions.versions = [version.parse(runtime.version) for runtime in versions]
            if versions.versions > latest[language]:
                latest[language] = versions.versions

    for data in matrix_data.values():
        for language, versions in data.items():
            versions.is_latest = versions.versions == latest[language]

    matrix_judges = sorted(matrix_data.keys())
    matrix_languages = sorted(languages, key=lambda lang: lang.key)

    return render(request, 'status/status.html', {
        'title': _('Status'),
        'judges': judges,
        'runtime_version_data': Judge.runtime_versions(),
        'see_all_judges': see_all,
        'languages': languages,
        'matrix_judges': matrix_judges,
        'matrix_languages': matrix_languages,
        'matrix': matrix_data,
    })


def status_oj(request):
    if not request.user.is_superuser:
        return HttpResponseBadRequest(_('You must be admin to view this content.'), content_type='text/plain')

    return render(request, 'status/oj-status.html', {
        'title': _('OJ Status'),
    })


def status_table(request):
    see_all, judges = get_judges(request)
    return render(request, 'status/judge-status-table.html', {
        'judges': judges,
        'runtime_version_data': Judge.runtime_versions(),
        'see_all_judges': see_all,
    })


class LatestList(list):
    __slots__ = ('versions', 'is_latest')


def compare_version_list(x, y):
    if sorted(x.keys()) != sorted(y.keys()):
        return False
    for k in x.keys():
        if len(x[k]) != len(y[k]):
            return False
        for a, b in zip(x[k], y[k]):
            if a.name != b.name:
                return False
            if a.version != b.version:
                return False
    return True
