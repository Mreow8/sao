from django.apps import AppConfig

class MainpageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainpage'

    # --- ADD THIS FUNCTION ---
    def ready(self):
        # This tells Django to load your new signals.py file
        import mainpage.signals