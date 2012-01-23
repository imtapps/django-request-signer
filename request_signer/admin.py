
from django import forms
from django.contrib import admin

from request_signer.models import AuthorizedClient

class AuthorizedClientForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AuthorizedClientForm, self).__init__(*args, **kwargs)
        self.fields['private_key'].widget.attrs['readonly'] = 'readonly'
        self.fields['private_key'].widget.attrs['style'] = 'width: 300px; background-color: #ccc;'

    class Meta(object):
        model = AuthorizedClient

class AuthorizedClientAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'is_active', 'created', 'updated']
    fields = ['client_id', 'private_key', 'is_active']
    form = AuthorizedClientForm

admin.site.register(AuthorizedClient, AuthorizedClientAdmin)