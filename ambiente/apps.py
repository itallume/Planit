from django.apps import AppConfig


class AmbienteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ambiente'
    
    def ready(self):
        """Importa signals quando a app estiver pronta"""
        import ambiente.signals
