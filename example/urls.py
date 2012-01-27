from django.conf.urls.defaults import patterns, include, url
from request_signer import signature_required
from django.contrib import admin
from server import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'sample/',  signature_required(views.SampleView.as_view())),
)
