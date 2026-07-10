from django.shortcuts import render

from judge.models import Language, RuntimeVersion


def status_all(request):
    languages = Language.objects.filter(runtime_versions__isnull=False).distinct()
    
    context = {
        'languages': languages,
    }
    
    return render(request, 'status/status.html', context)
