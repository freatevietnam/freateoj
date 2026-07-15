from django.conf import settings
from django.core.management.base import BaseCommand

from judge.models.relationship import RelationshipType


class Command(BaseCommand):
    help = 'Sync relationship types with settings.py'

    def handle(self, *args, **options):
        configured = getattr(settings, 'FREATEOJ_RELATIONSHIP_TYPES', {})
        existing = {rt.key: rt for rt in RelationshipType.objects.all()}

        # Add new types from settings
        for key, config in configured.items():
            if key in existing:
                rt = existing[key]
                changed = False
                if rt.name != config['name']:
                    rt.name = config['name']
                    changed = True
                if rt.max_per_user != config['max_per_user']:
                    rt.max_per_user = config['max_per_user']
                    changed = True
                if changed:
                    rt.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated: {config["name"]}'))
                else:
                    self.stdout.write(f'Unchanged: {config["name"]}')
            else:
                RelationshipType.objects.create(
                    key=key,
                    name=config['name'],
                    max_per_user=config['max_per_user']
                )
                self.stdout.write(self.style.SUCCESS(f'Created: {config["name"]}'))

        # Delete types not in settings
        for key, rt in existing.items():
            if key not in configured:
                rt.delete()
                self.stdout.write(self.style.WARNING(f'Deleted: {rt.name}'))

        self.stdout.write(self.style.SUCCESS('Done!'))
