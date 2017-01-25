# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'QueueUpdate'
        db.delete_table('rooms_queueupdate')


    def backwards(self, orm):
        
        # Adding model 'QueueUpdate'
        db.create_table('rooms_queueupdate', (
            ('kind', self.gf('django.db.models.fields.IntegerField')()),
            ('kind_id', self.gf('django.db.models.fields.IntegerField')()),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Queue'])),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('rooms', ['QueueUpdate'])


    models = {
        'rooms.building': {
            'Meta': {'object_name': 'Building'},
            'availname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'draw': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['rooms.Draw']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lon': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'pdfname': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'rooms.carrier': {
            'Meta': {'object_name': 'Carrier'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'rooms.draw': {
            'Meta': {'object_name': 'Draw'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '24'})
        },
        'rooms.pastdraw': {
            'Meta': {'object_name': 'PastDraw'},
            'draw': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Draw']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numpeople': ('django.db.models.fields.IntegerField', [], {}),
            'numrooms': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'rooms.pastdrawentry': {
            'Meta': {'object_name': 'PastDrawEntry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pastdraw': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.PastDraw']"}),
            'peoplerank': ('django.db.models.fields.IntegerField', [], {}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Room']"}),
            'roomrank': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {})
        },
        'rooms.photo': {
            'Meta': {'object_name': 'Photo'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        'rooms.queue': {
            'Meta': {'object_name': 'Queue'},
            'draw': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Draw']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'update_kind': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'update_user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['rooms.User']", 'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'rooms.queueinvite': {
            'Meta': {'object_name': 'QueueInvite'},
            'draw': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Draw']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'q_received_set'", 'to': "orm['rooms.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'q_sent_set'", 'to': "orm['rooms.User']"}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {})
        },
        'rooms.queuetoroom': {
            'Meta': {'object_name': 'QueueToRoom'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Queue']"}),
            'ranking': ('django.db.models.fields.IntegerField', [], {}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Room']"})
        },
        'rooms.review': {
            'Meta': {'object_name': 'Review'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Room']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.User']"})
        },
        'rooms.room': {
            'Meta': {'object_name': 'Room'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ada': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'adjacent': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'avail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bathroom': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'bi': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Building']"}),
            'con': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'floor': ('django.db.models.fields.IntegerField', [], {}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'numrooms': ('django.db.models.fields.IntegerField', [], {}),
            'occ': ('django.db.models.fields.IntegerField', [], {}),
            'sqft': ('django.db.models.fields.IntegerField', [], {}),
            'subfree': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated': ('django.db.models.fields.DateField', [], {})
        },
        'rooms.user': {
            'Meta': {'object_name': 'User'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Carrier']", 'null': 'True', 'blank': 'True'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'do_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'do_text': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'netid': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'puclassyear': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pustatus': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'queues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['rooms.Queue']", 'symmetrical': 'False'}),
            'seen_welcome': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['rooms']
