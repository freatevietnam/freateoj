from django.db import models
from django.utils.translation import gettext_lazy as _


class RelationshipType(models.Model):
    RELATIONSHIP_CHOICES = [
        ('tri_ky', _('Tri kỷ')),
        ('chi_em', _('Chị em')),
        ('ban_be', _('Bạn bè')),
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
