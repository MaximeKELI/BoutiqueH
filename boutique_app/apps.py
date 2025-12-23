from django.apps import AppConfig


class BoutiqueAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boutique_app'
    verbose_name = "La Gloire de Dieu - Boutique"
    
    def ready(self):
        import boutique_app.signals  # Import des signaux
