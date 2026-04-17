from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RewardsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rewards_app'
    verbose_name = _('Student Reward System')

    def ready(self):
        """Import signals when app is ready"""
        import rewards_app.models  # noqa
