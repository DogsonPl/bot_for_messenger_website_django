from django.apps import AppConfig
from django.conf import settings


class CasinoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'casino'

    def ready(self):
        from . import signals
        if settings.DEBUG:
            # on production gunicorn is responsible for running scheduler and collecting statistic data to cache
            from utils import scheduler, statistic_data
            scheduler.init()
            statistic_data.init()
