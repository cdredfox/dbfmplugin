#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import rhythmdb, rb,gobject
import libdbfm
from DoubanFMSource import DoubanFMSource
import logging,logging.handlers,gtk,gtk.glade
import Setup

channels = {_('Personalized'):0, _('Mandarin'):1, _('Western'):2, 
		            _('Cantonese'): 6, _('70s'): 3, _('80s'): 4, _('90s'): 5}

class DoubanFM(rb.Plugin):
	
	def __init__(self):
		rb.Plugin.__init__(self)

	def activate(self, shell):
		self._setup=Setup.SetupBox()
		self._handler = [
			shell.props.shell_player.connect('playing-song-changed', self._on_playing_song_changed)]
		self.db = shell.get_property("db")
		self.entry_type = self.db.entry_register_type("DoubanFMEntryType")
		# allow changes which don't do anything
		self.entry_type.can_sync_metadata = True
		self.entry_type.sync_metadata = None
		group = rb.rb_source_group_get_by_name ("stores")
		print self.entry_type
		self.source =gobject.new(DoubanFMSource,
					   shell=shell,
					   entry_type=self.entry_type,
					   plugin=self,
					   source_group=group)
		shell.register_entry_type_for_source(self.source, self.entry_type)
		shell.append_source(self.source, None) 
	
	def _on_playing_song_changed(self, player, entry):
		print self.source.__songSize__
		self.source.__songSize__=self.source.__songSize__-1
		if self.source.__songSize__<1:
			self.source.resetSongs()		
	
	def create_configure_dialog(self):
		self._setup.present()
		return self._setup
	def deactivate(self, shell):
		self.db.entry_delete_by_type(self.entry_type)
		self.db.commit()
		self.db = None
		self.entry_type = None
		self.source.delete_thyself()
		self.source = None
		
