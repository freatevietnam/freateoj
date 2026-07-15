from django.conf import settings
from django.core.management.base import BaseCommand

from judge.models.relationship import RelationshipType


class Command(BaseCommand):
    help = 'Initialize relationship types from settings'

    def handle(self, *args, **options):
        types = getattr(settings, 'FREATEOJ_RELATIONSHIP_TYPES', {})

        for key, config in types.items():
            RelationshipType.objects.update_or_create(
                key=key,
                defaults={
                    'name': config['name'],
                    'max_per_user': config['max_per_user']
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Created/Updated relationship type: {config["name"]}'))

        self.stdout.write(self.style.SUCCESS('Done!'))
