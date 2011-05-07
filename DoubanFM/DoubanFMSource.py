# -*- coding: utf-8 -*-


import rb, rhythmdb
import os
import gobject
import gtk
import gnome, gconf
import xml
import gzip
import datetime
import libdbfm
import logging,logging.handlers

log=logging.getLogger('DoubanFM')

USER_NAME_KEY='/rhythmbox.plugin.doubanfm.username'
USER_PWD_KEY='/rhythmbox.plugin.doubanfm.userpwd'
class DoubanFMSource(rb.BrowserSource):
	__songSize__=0;
	__gproperties__ = {
		'plugin': (rb.Plugin, 'plugin', 'plugin', gobject.PARAM_WRITABLE|gobject.PARAM_CONSTRUCT_ONLY),
	}

	
	def set_channel(self,channel):
		self.__channel=channel

	def __init__(self):
		rb.BrowserSource.__init__(self, name=_("豆瓣电台"))
		
		self.__activated = False
		self.__db = None # rhythmdb
		self.__notify_id = 0 # gobject.idle_add id for status notifications
		self.__info_screen = None # the loading screen
		self.__channel=0
		self.__userName=gconf.client_get_default().get_without_default(USER_NAME_KEY).get_string()
		self.__userPWD=gconf.client_get_default().get_without_default(USER_PWD_KEY).get_string()
		log.info("_userName:"+self.__userName);

	def do_set_property(self, property, value):
		if property.name == 'plugin':
			self.__plugin = value
		else:
			raise AttributeError, 'unknown property %s' % property.name

	def do_selected(self):
			if not self.__activated:
					self.__shell=self.get_property('shell')
					self.__db=self.__shell.get_property('db')
					self.__entry_type=self.get_property('entry-type')
					self.__activated = True
			self.resetSongs()
	def add_Song(self,song):
		entry = self.__db.entry_lookup_by_location (song.url)
		if entry == None:
			entry = self.__db.entry_new(self.__entry_type, song.url)
		log.info(song.company)		
		self.__db.set(entry, rhythmdb.PROP_TITLE,song.title)
		self.__db.set(entry, rhythmdb.PROP_ALBUM, song.albumtitle)
		self.__db.set(entry,rhythmdb.PROP_GENRE,'' if song.company==None else song.company)
		self.__db.set(entry,rhythmdb.PROP_ALBUM,song.albumtitle)
		
	def get_Songs(self):	
			self.doubanfm=libdbfm.DoubanFM(self.__userName,self.__userPWD)
			self.doubanfm.channel=self.__channel
			songs=self.doubanfm.new_playlist()
			return songs
	def resetSongs(self):
		self.removeList()
		self.songsMap={"title":"title"}
		songs=self.get_Songs()
		log.info(len(songs))
		self.__songSize__=len(songs)
		for song in songs:
			self.songsMap[song.title]=song
			self.add_Song(song)
		self.__db.commit()
	
	def removeList(self):
		log.info("remove list")
		for row in self.props.query_model:
			entry = row[0]
 			log.info(self.__db.entry_get(entry, rhythmdb.PROP_TITLE))
		 	self.__db.entry_delete(entry);
gobject.type_register(DoubanFMSource)

