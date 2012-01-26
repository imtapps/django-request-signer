from django.conf.urls.defaults import patterns, include, url

from request_signer import signature_required
from server import views

urlpatterns = patterns('',
    url(r'sample/',  signature_required(views.SampleView.as_view())),
)
