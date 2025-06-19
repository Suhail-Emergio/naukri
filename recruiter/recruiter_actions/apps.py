from django.apps import AppConfig


class RecruiterActionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recruiter_actions'

    def ready(self):
        import recruiter.recruiter_actions.signals