from django.http import JsonResponse

from judge.jinja2.gravatar import gravatar
from judge.models import Profile


def user_summary(request, username):
    """AJAX endpoint to get user summary data for popup."""
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Get gravatar URL
    avatar_url = gravatar(profile.user.email, 96)
    
    data = {
        'username': profile.user.username,
        'display_name': profile.display_name,
        'rating': profile.rating,
        'rank': profile.display_rank,
        'problems_solved': profile.problem_count,
        'performance_points': profile.performance_points,
        'join_date': profile.user.date_joined.strftime('%d/%m/%Y'),
        'last_login': profile.user.last_login.strftime('%d/%m/%Y') if profile.user.last_login else None,
        'avatar_url': avatar_url,
        'about': profile.about if hasattr(profile, 'about') else '',
        'profile_url': f'/user/{profile.user.username}/',
    }
    
    return JsonResponse(data)
