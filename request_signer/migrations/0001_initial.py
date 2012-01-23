# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AuthorizedClient'
        db.create_table('request_signer_authorizedclient', (
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('private_key', self.gf('django.db.models.fields.CharField')(default='ZTWXjy01_v-muyWoLMSYOteEniKiPuqVim1ah_dfd2A=', max_length=100)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('request_signer', ['AuthorizedClient'])


    def backwards(self, orm):
        
        # Deleting model 'AuthorizedClient'
        db.delete_table('request_signer_authorizedclient')


    models = {
        'request_signer.authorizedclient': {
            'Meta': {'object_name': 'AuthorizedClient'},
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'private_key': ('django.db.models.fields.CharField', [], {'default': "'jAqUpViHFDNVg0IhGSaXxsi1RrhO9hHpmvUuiRr0q6I='", 'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['request_signer']
