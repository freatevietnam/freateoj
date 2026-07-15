from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from judge.models.relationship import Relationship, RelationshipType


class RelationshipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'max_per_user')
    list_filter = ('key',)
    search_fields = ('name',)


class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'relationship_type', 'status', 'pending_type_change', 'created_at')
    list_filter = ('status', 'relationship_type')
    search_fields = ('from_user__user__username', 'to_user__user__username')
    raw_id_fields = ('from_user', 'to_user', 'relationship_type', 'pending_type_change')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'from_user__user', 'to_user__user', 'relationship_type', 'pending_type_change'
        )


admin.site.register(RelationshipType, RelationshipTypeAdmin)
admin.site.register(Relationship, RelationshipAdmin)
