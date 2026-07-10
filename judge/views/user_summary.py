import json
from datetime import datetime, timedelta

from django.db.models import Count, F
from django.db.models.fields import DateField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.utils import timezone

from judge.jinja2.gravatar import gravatar
from judge.models import Profile, Submission


def user_summary(request, username):
    """AJAX endpoint to get user summary data for popup."""
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Get gravatar URL
    avatar_url = gravatar(profile.user.email, 96)
    
    # Get submission activity data (last year)
    utc_offset = timezone_offset = timezone.now().astimezone().utcoffset().total_seconds()
    one_year_ago = timezone.now() - timedelta(days=365)
    
    submissions = (
        Submission.objects
        .filter(user=profile, date__gte=one_year_ago)
        .annotate(date_only=Cast(F('date') + timedelta(seconds=timezone_offset), DateField()))
        .values('date_only')
        .annotate(cnt=Count('id'))
    )
    
    submission_activity = {
        date_counts['date_only'].isoformat(): date_counts['cnt'] 
        for date_counts in submissions
    }
    
    data = {
        'username': profile.user.username,
        'display_name': profile.display_name,
        'rating': profile.rating,
        'rank': profile.display_rank,
        'problems_solved': profile.problem_count,
        'performance_points': profile.performance_points,
        'avatar_url': avatar_url,
        'about': profile.about if hasattr(profile, 'about') else '',
        'profile_url': f'/user/{profile.user.username}/',
        'submission_activity': submission_activity,
    }
    
    return JsonResponse(data)
