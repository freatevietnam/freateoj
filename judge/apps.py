from django.apps import AppConfig
from django.db import DatabaseError
from django.utils.translation import gettext_lazy


class JudgeAppConfig(AppConfig):
    name = 'judge'
    verbose_name = gettext_lazy('Online Judge')

    def ready(self):
        # WARNING: AS THIS IS NOT A FUNCTIONAL PROGRAMMING LANGUAGE,
        #          OPERATIONS MAY HAVE SIDE EFFECTS.
        #          DO NOT REMOVE THINKING THE IMPORT IS UNUSED.
        # noinspection PyUnresolvedReferences
        from . import signals, jinja2  # noqa: F401, imported for side effects

        from judge.models import Language, Profile
        from django.contrib.auth.models import User

        try:
            lang = Language.get_default_language()
            for user in User.objects.filter(profile=None):
                # These poor profileless users
                profile = Profile(user=user, language=lang)
                profile.save()
        except DatabaseError:
            pass

        # Auto-sync relationship types from settings
        self._sync_relationship_types()

    def _sync_relationship_types(self):
        from django.conf import settings
        from judge.models.relationship import RelationshipType

        configured = getattr(settings, 'FREATEOJ_RELATIONSHIP_TYPES', {})
        if not configured:
            return

        try:
            existing = {rt.key: rt for rt in RelationshipType.objects.all()}

            for key, config in configured.items():
                if key in existing:
                    rt = existing[key]
                    if rt.name != config['name'] or rt.max_per_user != config['max_per_user']:
                        rt.name = config['name']
                        rt.max_per_user = config['max_per_user']
                        rt.save()
                else:
                    RelationshipType.objects.create(
                        key=key,
                        name=config['name'],
                        max_per_user=config['max_per_user']
                    )

            for key, rt in existing.items():
                if key not in configured:
                    rt.delete()
        except DatabaseError:
            pass
