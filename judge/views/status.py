from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from judge.models import Language


def status_all(request):
    languages = Language.objects.filter(runtimeversion__isnull=False).distinct()
    
    context = {
        'languages': languages,
    }
    
    return render(request, 'status/status.html', context)


def status_table(request):
    """AJAX endpoint to get updated judge status table."""
    html = render_to_string('status/judge-status-table.html')
    return JsonResponse({'html': html})
