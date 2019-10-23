from django.apps import AppConfig


class RsexamplesConfig(AppConfig):
    name = 'rsexamples'

    def ready(self):
        import rsexamples.signals
