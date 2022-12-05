import django

if django.get_version() >= '2.0.0':
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from django.contrib import admin
from django import http

from request_signer.decorators import signature_required

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/$', signature_required(lambda request, *args, **kwargs: http.HttpResponse("Completed Test View!"))),
    url(r'^test/(?P<arg>.*)/$', signature_required(lambda request, *args, **kwargs: http.HttpResponse("X")))
]
