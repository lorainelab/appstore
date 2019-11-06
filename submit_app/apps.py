from django.apps import AppConfig


class SubmitAppConfig(AppConfig):
    name = 'submit_app'

    def ready(self):
        from submit_app import app_pending_cleanup
        app_pending_cleanup.start()
