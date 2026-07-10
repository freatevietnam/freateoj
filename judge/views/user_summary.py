from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from judge.models import Profile


def user_summary(request, username):
    """AJAX endpoint to get user summary data for popup."""
    profile = get_object_or_404(Profile, user__username=username)
    
    data = {
        'username': profile.user.username,
        'display_name': profile.display_name,
        'rating': profile.rating,
        'rank': profile.display_rank,
        'problems_solved': profile.solved,
        'problems_attempted': profile.total,
        'performance_points': profile.performance_points,
        'join_date': profile.user.date_joined.strftime('%d/%m/%Y'),
        'last_login': profile.user.last_login.strftime('%d/%m/%Y') if profile.user.last_login else None,
        'avatar_url': profile.avatar_url if hasattr(profile, 'avatar_url') else None,
        'about': profile.about if hasattr(profile, 'about') else '',
        'profile_url': f'/user/{profile.user.username}/',
    }
    
    return JsonResponse(data)
