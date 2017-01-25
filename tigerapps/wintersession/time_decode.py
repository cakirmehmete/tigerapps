'''
Created on Dec 25, 2013

@author: elan
'''

def decode(timecode):
    time = timecode % 1000
    dowc = (timecode - (time))/1000
    dow = "X"
    if dowc == 0:
        dow = "Sunday"
    elif dowc == 1:
        dow = "Monday"
    elif dowc == 2:
        dow = "Tuesday"
    elif dowc == 3:
        dow = "Wednesday"
    elif dowc == 4:
        dow = "Thursday"
    elif dowc == 5:
        dow = "Friday"
    elif dowc == 6:
        dow = "Saturday"

    if str(time)[-1] == '5':
        half = ":30"
    else:
        half = ""

    if time / 10 > 12:
        hour = time / 10 - 12
        merid = "p"
    elif time / 10 == 12:
        hour = 12
        merid = 'p'
    else:
        hour = time / 10
        merid = "a"

    return dow+" "+str(hour)+half+merid

def decode_time(time):
    if str(time)[-1] == '5':
        half = ":30"
    else:
        half = ""

    if time / 10 > 12:
        hour = time / 10 - 12
        merid = "p"
    elif time / 10 == 12:
        hour = 12
        merid = 'p'
    else:
        hour = time / 10
        merid = "a"

    return str(hour)+half+merid
