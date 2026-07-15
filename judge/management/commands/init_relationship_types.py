from django.core.management.base import BaseCommand

from judge.models.relationship import RelationshipType


class Command(BaseCommand):
    help = 'Initialize relationship types'

    def handle(self, *args, **options):
        types = [
            ('tri_ky', 'Tri kỷ', 5),
            ('chi_em', 'Chị em', 5),
            ('ban_be', 'Bạn bè', 5),
            ('cap_doi', 'Cặp đôi', 1),
            ('lop_du_phong', 'Lốp dự phòng', 999),
        ]

        for key, name, max_per_user in types:
            RelationshipType.objects.get_or_create(
                key=key,
                defaults={'name': name, 'max_per_user': max_per_user}
            )
            self.stdout.write(self.style.SUCCESS(f'Created relationship type: {name}'))

        self.stdout.write(self.style.SUCCESS('Done!'))
