from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class RelationshipType(models.Model):
    RELATIONSHIP_CHOICES = [
        ('tri_ky', _('Tri kỷ')),
        ('chi_em', _('Chị em')),
        ('anh_em', _('Anh em')),
        ('cap_doi', _('Cặp đôi')),
        ('lop_du_phong', _('Lốp dự phòng')),
    ]

    key = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, unique=True)
    name = models.CharField(max_length=50, verbose_name=_('relationship name'))
    max_per_user = models.IntegerField(verbose_name=_('max per user'), default=5)

    class Meta:
        verbose_name = _('relationship type')
        verbose_name_plural = _('relationship types')

    def __str__(self):
        return self.name


class Relationship(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
    ]

    from_user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='relationships_sent')
    to_user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='relationships_received')
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For type change requests
    pending_type_change = models.ForeignKey(RelationshipType, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='pending_type_changes')

    class Meta:
        verbose_name = _('relationship')
        verbose_name_plural = _('relationships')
        unique_together = ('from_user', 'to_user', 'relationship_type')
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'],
                condition=models.Q(status='accepted'),
                name='unique_accepted_relationship_per_pair'
            )
        ]

    def __str__(self):
        return f'{self.from_user} -> {self.to_user} ({self.relationship_type})'

    def accept(self):
        self.status = 'accepted'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def request_type_change(self, new_type):
        self.pending_type_change = new_type
        self.save()

    def accept_type_change(self):
        if self.pending_type_change:
            self.relationship_type = self.pending_type_change
            self.pending_type_change = None
            self.save()

    def reject_type_change(self):
        self.pending_type_change = None
        self.save()

    @classmethod
    def cleanup_duplicates(cls):
        """Auto-fix: Remove duplicate relationships, keep only the newest."""
        from django.db.models import Q

        relationships = cls.objects.filter(status='accepted').order_by('-created_at')
        seen_pairs = set()
        to_delete = []

        for rel in relationships:
            pair = tuple(sorted([rel.from_user_id, rel.to_user_id]))
            if pair in seen_pairs:
                to_delete.append(rel.id)
            else:
                seen_pairs.add(pair)

        if to_delete:
            cls.objects.filter(id__in=to_delete).delete()
            return len(to_delete)
        return 0

    @classmethod
    def cleanup_old_pending(cls):
        """Auto-fix: Remove old pending requests when newer ones exist."""
        from django.db.models import Q

        pending = cls.objects.filter(status='pending')
        to_delete = []

        for rel in pending:
            newer_exists = cls.objects.filter(
                from_user=rel.from_user,
                to_user=rel.to_user,
                created_at__gt=rel.created_at
            ).exists()
            if newer_exists:
                to_delete.append(rel.id)

        if to_delete:
            cls.objects.filter(id__in=to_delete).delete()
            return len(to_delete)
        return 0

    @classmethod
    def has_any_relationship(cls, user1, user2):
        """Check if any accepted relationship exists between two users."""
        return cls.objects.filter(
            Q(from_user=user1, to_user=user2, status='accepted') |
            Q(from_user=user2, to_user=user1, status='accepted')
        ).exists()

    @classmethod
    def can_add(cls, user, relationship_type):
        count = cls.objects.filter(
            models.Q(from_user=user) | models.Q(to_user=user),
            relationship_type=relationship_type,
            status='accepted'
        ).count()
        return count < relationship_type.max_per_user

    @classmethod
    def get_relationships(cls, user):
        return cls.objects.filter(
            models.Q(from_user=user) | models.Q(to_user=user),
            status='accepted'
        ).select_related('from_user__user', 'to_user__user', 'relationship_type', 'pending_type_change')
