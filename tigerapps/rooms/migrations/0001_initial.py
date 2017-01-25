# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Draw'
        db.create_table('rooms_draw', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=24)),
        ))
        db.send_create_signal('rooms', ['Draw'])

        # Adding model 'Building'
        db.create_table('rooms_building', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('pdfname', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('availname', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('lon', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('rooms', ['Building'])

        # Adding M2M table for field draw on 'Building'
        db.create_table('rooms_building_draw', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('building', models.ForeignKey(orm['rooms.building'], null=False)),
            ('draw', models.ForeignKey(orm['rooms.draw'], null=False))
        ))
        db.create_unique('rooms_building_draw', ['building_id', 'draw_id'])

        # Adding model 'Room'
        db.create_table('rooms_room', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('sqft', self.gf('django.db.models.fields.IntegerField')()),
            ('occ', self.gf('django.db.models.fields.IntegerField')()),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Building'])),
            ('subfree', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('numrooms', self.gf('django.db.models.fields.IntegerField')()),
            ('floor', self.gf('django.db.models.fields.IntegerField')()),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('avail', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('adjacent', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('ada', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bi', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('con', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bathroom', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('rooms', ['Room'])

        # Adding model 'User'
        db.create_table('rooms_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('netid', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('pustatus', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('puclassyear', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('do_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('do_text', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Carrier'], null=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rooms', ['User'])

        # Adding M2M table for field queues on 'User'
        db.create_table('rooms_user_queues', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['rooms.user'], null=False)),
            ('queue', models.ForeignKey(orm['rooms.queue'], null=False))
        ))
        db.create_unique('rooms_user_queues', ['user_id', 'queue_id'])

        # Adding model 'Queue'
        db.create_table('rooms_queue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('draw', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Draw'])),
        ))
        db.send_create_signal('rooms', ['Queue'])

        # Adding model 'QueueToRoom'
        db.create_table('rooms_queuetoroom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Queue'])),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Room'])),
            ('ranking', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('rooms', ['QueueToRoom'])

        # Adding model 'QueueUpdate'
        db.create_table('rooms_queueupdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Queue'])),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')()),
            ('kind', self.gf('django.db.models.fields.IntegerField')()),
            ('kind_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('rooms', ['QueueUpdate'])

        # Adding model 'QueueInvite'
        db.create_table('rooms_queueinvite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='q_sent_set', to=orm['rooms.User'])),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='q_received_set', to=orm['rooms.User'])),
            ('draw', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Draw'])),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('rooms', ['QueueInvite'])

        # Adding model 'Review'
        db.create_table('rooms_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Room'])),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.User'])),
        ))
        db.send_create_signal('rooms', ['Review'])

        # Adding model 'Photo'
        db.create_table('rooms_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('rooms', ['Photo'])

        # Adding model 'PastDraw'
        db.create_table('rooms_pastdraw', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('draw', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Draw'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('numrooms', self.gf('django.db.models.fields.IntegerField')()),
            ('numpeople', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('rooms', ['PastDraw'])

        # Adding model 'PastDrawEntry'
        db.create_table('rooms_pastdrawentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pastdraw', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.PastDraw'])),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rooms.Room'])),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')()),
            ('roomrank', self.gf('django.db.models.fields.IntegerField')()),
            ('peoplerank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('rooms', ['PastDrawEntry'])

        # Adding model 'Carrier'
        db.create_table('rooms_carrier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('rooms', ['Carrier'])


    def backwards(self, orm):
        
        # Deleting model 'Draw'
        db.delete_table('rooms_draw')

        # Deleting model 'Building'
        db.delete_table('rooms_building')

        # Removing M2M table for field draw on 'Building'
        db.delete_table('rooms_building_draw')

        # Deleting model 'Room'
        db.delete_table('rooms_room')

        # Deleting model 'User'
        db.delete_table('rooms_user')

        # Removing M2M table for field queues on 'User'
        db.delete_table('rooms_user_queues')

        # Deleting model 'Queue'
        db.delete_table('rooms_queue')

        # Deleting model 'QueueToRoom'
        db.delete_table('rooms_queuetoroom')

        # Deleting model 'QueueUpdate'
        db.delete_table('rooms_queueupdate')

        # Deleting model 'QueueInvite'
        db.delete_table('rooms_queueinvite')

        # Deleting model 'Review'
        db.delete_table('rooms_review')

        # Deleting model 'Photo'
        db.delete_table('rooms_photo')

        # Deleting model 'PastDraw'
        db.delete_table('rooms_pastdraw')

        # Deleting model 'PastDrawEntry'
        db.delete_table('rooms_pastdrawentry')

        # Deleting model 'Carrier'
        db.delete_table('rooms_carrier')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        'rooms.queueupdate': {
            'Meta': {'object_name': 'QueueUpdate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.IntegerField', [], {}),
            'kind_id': ('django.db.models.fields.IntegerField', [], {}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Queue']"}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {})
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
            'subfree': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'rooms.user': {
            'Meta': {'object_name': 'User'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rooms.Carrier']", 'null': 'True'}),
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
            'queues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['rooms.Queue']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['rooms']
