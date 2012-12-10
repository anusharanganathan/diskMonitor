# -*- coding: utf-8 -*-
"""
    Disk monitor Task

    A Celery task used to run the file monitor which creates, updates or deletes entries
    in a database containing file information everytime a file is created, modified 
    or deleted. The monitoring of files is done using inotify.

    Copyright: (c) 2012 by Anusha Ranganathan.
"""

from __future__ import absolute_import
import pyinotify
from celery import Celery
import os, stat, time

from dbHandler import dbHandler
from diskMonitorConfig import SCAN_LOCATIONS, DATABASE, TABLE
import celeryconfig

celery = Celery()
celery.config_from_object(celeryconfig)
db = dbHandler(database=DATABASE, table=TABLE)


class EventHandler(pyinotify.ProcessEvent):

    def bytes_to_english(self, no_of_bytes):
        #Helper function to convert number of bytes receives from os.stat into human radabale form
        # 1024 per 'level'
        suffixes = ['bytes', 'kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Yb']
        f_no = float(no_of_bytes)
        level = 0
        while(f_no > 1024.0):
            f_no = f_no / 1024.0
            level = level + 1
        if level == 0:
            return "%s %s" % (no_of_bytes, suffixes[level])
        return "%5.1f %s" % (f_no, suffixes[level])

    def getStats(self, pathname, name):
        #Helper function to form the data dictionary for passing onto the database helper.
        stats = os.stat(pathname)
        filestats = {'path':pathname, 'name':name}
        filestats['ATime'] = time.strftime("%d-%m-%Y %H:%M:%S",time.localtime(stats[stat.ST_ATIME]))
        filestats['CTime'] = time.strftime("%d-%m-%Y %H:%M:%S",time.localtime(stats[stat.ST_CTIME]))
        filestats['MTime'] = time.strftime("%d-%m-%Y %H:%M:%S",time.localtime(stats[stat.ST_MTIME]))
        filestats['size'] = stats[stat.ST_SIZE]
        filestats['size_human'] = self.bytes_to_english(stats[stat.ST_SIZE])
        if stat.S_ISDIR(stats[stat.ST_MODE]):
            filestats['type'] = 'Directory'
        elif stat.S_ISLNK(stats[stat.ST_MODE]):
            filestats['type'] = 'Symbolic link'
        else:
            filestats['type'] = 'File'
        return filestats

    def process_IN_CREATE(self, event):
        #Called everytime a file / dir is created
        filestats = self.getStats(event.pathname, event.name)
        db.create(filestats)
 
    def process_IN_DELETE(self, event):
        #Called everytime a file / dir is deleted
        db.delete(event.pathname)

    def process_IN_MODIFY(self, event):
        #Called everytime a file / dir is modified
        filestats = self.getStats(event.pathname, event.name)
        db.modify(filestats)

@celery.task
def monitorDisk():
    #Initialize the inotify watch manager
    wm = pyinotify.WatchManager()
    # watched events
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY 
    notifier = pyinotify.Notifier(wm, EventHandler())
    for location in SCAN_LOCATIONS:
        wdd = wm.add_watch(location, mask, rec=True)
    notifier.loop()

