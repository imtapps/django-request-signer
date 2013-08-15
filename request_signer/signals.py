import django.dispatch

successful_signed_request = django.dispatch.Signal(providing_args=['request'])
