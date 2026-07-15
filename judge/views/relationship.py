from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from judge.models import Profile
from judge.models.relationship import Relationship, RelationshipType


@login_required
def send_relationship_request(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    to_user = get_object_or_404(Profile, user__username=username)
    from_user = request.profile

    if from_user == to_user:
        return JsonResponse({'error': _('Cannot send request to yourself')}, status=400)

    relationship_type_id = request.POST.get('relationship_type')
    if not relationship_type_id:
        return JsonResponse({'error': _('Relationship type is required')}, status=400)

    relationship_type = get_object_or_404(RelationshipType, id=relationship_type_id)

    # Check if can add more
    if not Relationship.can_add(from_user, relationship_type):
        max_limit = relationship_type.max_per_user
        return JsonResponse({'error': _('You have reached the limit of %(count)s for this type', count=max_limit)}, status=400)

    # Check if already exists (in either direction)
    existing = Relationship.objects.filter(
        from_user=from_user,
        to_user=to_user,
        relationship_type=relationship_type
    ).first()

    if existing:
        if existing.status == 'pending':
            return JsonResponse({'error': _('Request already pending')}, status=400)
        elif existing.status == 'accepted':
            return JsonResponse({'error': _('Already friends')}, status=400)
        else:
            # Rejected, allow new request
            existing.delete()

    # Check if reverse relationship exists
    reverse_existing = Relationship.objects.filter(
        from_user=to_user,
        to_user=from_user,
        relationship_type=relationship_type
    ).first()

    if reverse_existing:
        if reverse_existing.status == 'pending':
            return JsonResponse({'error': _('Request already pending from this user')}, status=400)
        elif reverse_existing.status == 'accepted':
            return JsonResponse({'error': _('Already friends')}, status=400)
        else:
            # Rejected, allow new request
            reverse_existing.delete()

    # Create request
    relationship = Relationship.objects.create(
        from_user=from_user,
        to_user=to_user,
        relationship_type=relationship_type
    )

    return JsonResponse({'success': True, 'message': _('Request sent successfully')})


@login_required
def accept_relationship(request, relationship_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    relationship = get_object_or_404(Relationship, id=relationship_id, to_user=request.profile, status='pending')

    # Check if can add more
    if not Relationship.can_add(request.user.profile, relationship.relationship_type):
        max_limit = relationship.relationship_type.max_per_user
        return JsonResponse({'error': _('You have reached the limit of %(count)s for this type', count=max_limit)}, status=400)

    # Check if reverse relationship already accepted
    reverse_accepted = Relationship.objects.filter(
        from_user=relationship.to_user,
        to_user=relationship.from_user,
        relationship_type=relationship.relationship_type,
        status='accepted'
    ).exists()

    if reverse_accepted:
        return JsonResponse({'error': _('Already friends')}, status=400)

    relationship.accept()
    return JsonResponse({'success': True, 'message': _('Request accepted')})


@login_required
def reject_relationship(request, relationship_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    relationship = get_object_or_404(Relationship, id=relationship_id, to_user=request.profile, status='pending')
    relationship.reject()
    return JsonResponse({'success': True, 'message': _('Request rejected')})


@login_required
def remove_relationship(request, relationship_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    relationship = get_object_or_404(Relationship, id=relationship_id)
    if relationship.from_user != request.profile and relationship.to_user != request.profile:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    relationship.delete()
    return JsonResponse({'success': True, 'message': _('Relationship removed')})


@login_required
def get_relationship_types(request):
    types = RelationshipType.objects.all()
    data = [{
        'id': t.id,
        'key': t.key,
        'name': t.name,
        'max_per_user': t.max_per_user
    } for t in types]
    return JsonResponse({'types': data})


@login_required
def get_pending_requests(request):
    requests = Relationship.objects.filter(
        to_user=request.profile,
        status='pending'
    ).select_related('from_user__user', 'relationship_type')

    data = [{
        'id': r.id,
        'from_user': r.from_user.user.username,
        'relationship_type': r.relationship_type.name,
        'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
    } for r in requests]

    return JsonResponse({'requests': data})


@login_required
def request_type_change(request, relationship_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    relationship = get_object_or_404(Relationship, id=relationship_id, status='accepted')
    if relationship.from_user != request.profile and relationship.to_user != request.profile:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    new_type_id = request.POST.get('new_type')
    if not new_type_id:
        return JsonResponse({'error': _('New type is required')}, status=400)

    new_type = get_object_or_404(RelationshipType, id=new_type_id)

    if new_type == relationship.relationship_type:
        return JsonResponse({'error': _('Same type as current')}, status=400)

    relationship.request_type_change(new_type)
    return JsonResponse({'success': True, 'message': _('Type change request sent')})


@login_required
def accept_type_change(request, relationship_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    relationship = get_object_or_404(Relationship, id=relationship_id, status='accepted')
    if relationship.to_user != request.profile:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    if not relationship.pending_type_change:
        return JsonResponse({'error': _('No pending type change')}, status=400)

    # Check if can add more of the new type
    if not Relationship.can_add(request.user.profile, relationship.pending_type_change):
        max_limit = relationship.pending_type_change.max_per_user
        return JsonResponse({'error': _('You have reached the limit of %(count)s for this type', count=max_limit)}, status=400)

    relationship.accept_type_change()
    return JsonResponse({'success': True, 'message': _('Type change accepted')})


@login_required
def reject_type_change(request, relationship_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    relationship = get_object_or_404(Relationship, id=relationship_id, status='accepted')
    if relationship.to_user != request.profile:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    relationship.reject_type_change()
    return JsonResponse({'success': True, 'message': _('Type change rejected')})
