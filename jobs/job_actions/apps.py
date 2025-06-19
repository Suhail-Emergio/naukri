from django.apps import AppConfig


class JobActionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_actions'

    def ready(self):
        import jobs.job_actions.signals