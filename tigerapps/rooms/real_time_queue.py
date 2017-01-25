import time
from rooms.models import Room, Draw, Queue, QueueToRoom, User, QueueInvite
from gevent import spawn, sleep
from gevent.event import Event
from gevent.coros import BoundedSemaphore
import subprocess
import os, sys
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

DEFAULT_CLEAR_INTERVAL = 10*60

class QueueUpdate(object):
    def __init__(self, queue_id):
        self.event = Event()
        self.queue = Queue.objects.get(pk=queue_id)

    def fresh(self):
        self.queue = Queue.objects.get(pk=self.queue.id)
        return self

class QueueManager(object):
    
    def __init__(self, clear_interval=DEFAULT_CLEAR_INTERVAL):
        self.__updates = {}
        self.__updates_lock = BoundedSemaphore()
        # Start clearing daemon thread.
        spawn(self._daemon_clear, interval=clear_interval)

    def _load(self, queue_id):
        """Load and return queue update tracker for queue_id."""
        self.__updates_lock.acquire()
        # Hit.
        if queue_id in self.__updates:
            self.__updates_lock.release()
            return self.__updates[queue_id].fresh()
        # Miss.
        self.__updates[queue_id] = QueueUpdate(queue_id)
        self.__updates_lock.release()
        return self.__updates[queue_id]

    def _clear(self):
        """Clear the in-memory update tracking dictionary"""
        self.__updates_lock.acquire()
        print 'Clearing'
        # Make sure anyone currently waiting reloads.
        for queue_id in self.__updates:
            self.__updates[queue_id].event.set()
            self.__updates[queue_id].event.clear()
        self.__updates = {}
        print 'Clear'
        self.__updates_lock.release()

    def _daemon_clear(self, interval):
        """Clear the update tracking dictionary every interval seconds."""
        while True:
            sleep(interval)
            self._clear()

    def edit(self, user, queue_id, room_idlist, draw):
        # Put together the list of Room objects.
        rooms = []
        print 'edit', room_idlist
        for roomid in room_idlist:
            room = Room.objects.get(pk=roomid)
            if (not room) or not draw in room.building.draw.all():
                return {'error':'bad room/draw'}
            rooms.append(room)
        
        update = self._load(queue_id)
        # Clear out the old list.
        queue = update.queue
        queue.queuetoroom_set.all().delete()
        # Put in new relationships
        for i in range(0, len(rooms)):
            qtr = QueueToRoom(queue=queue, room=rooms[i], ranking=i)
            qtr.save()
        # Store the update information on the queue.
        queue.version += 1
        queue.update_kind = Queue.EDIT
        queue.update_user = user
        queue.save()
        # Notify others of the update.
        update.event.set()
        update.event.clear()
        # Assemble and return response.
        room_list = []
        for room in rooms:
            room_list.append({'id':room.id, 'number':room.number,
                              'building':room.building.name})
        return {'rooms':room_list}

    def check(self, user, queue_id, last_version):
        update = self._load(queue_id)
        print user, update.queue, last_version
        if last_version == update.queue.version:
            print 'going to wait'
            print update.queue.version
            update.event.wait()
            update = self._load(queue_id)
        print 'past wait'
        queueToRooms = QueueToRoom.objects.filter(queue=update.queue).order_by('ranking')
        if not queueToRooms:
            return {'id':update.queue.version, 'rooms':[]}
        room_list = []
        if update.queue.update_user:
            netid = update.queue.update_user.netid
        else:
            netid = ''
        for qtr in queueToRooms:
            room_list.append({'id':qtr.room.id, 'number':qtr.room.number,
                              'building':qtr.room.building.name})
        return {'id':update.queue.version,
                'kind':Queue.UPDATE_KINDS[update.queue.update_kind][1],
                'netid':netid,
                'rooms':room_list}

manager = QueueManager()

def check(user, queue_id, last_version):
    print 'Check 1'
    print user, queue_id, last_version
    response = manager.check(user, queue_id, last_version)
    while response.get('netid') == user.netid and last_version != 0:
        response = manager.check(user, queue_id, response['id'])
    # Add in queue invitation notification.
    response['invites'] = QueueInvite.objects.filter(receiver=user).count()
    return response

edit = manager.edit
