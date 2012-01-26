from django import http
from django.views.generic.base import View

class SampleView(View):

    def get(self, request):
        return http.HttpResponse("hi")

    def post(self, request):
        return http.HttpResponse("hi")
