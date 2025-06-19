from django.apps import AppConfig


class JobpostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobposts'

    def ready(self):
        import jobs.jobposts.signals