from django.apps import AppConfig


class CommonActionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common_actions'

    def ready(self):
        import common_actions.signals