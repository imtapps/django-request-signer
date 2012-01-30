
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from request_signer.decorators import signature_required

from server import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'sample/',  signature_required(views.SampleView.as_view())),
)
