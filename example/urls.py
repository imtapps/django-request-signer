from django.conf.urls import include, url
from django.contrib import admin
from django import http

from request_signer.decorators import signature_required

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/$', signature_required(lambda request, *args, **kwargs: http.HttpResponse("Completed Test View!"))),
    url(r'^test/(?P<arg>.*)/$', signature_required(lambda request, *args, **kwargs: http.HttpResponse("X")))
]
