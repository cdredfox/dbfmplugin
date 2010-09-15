#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import rhythmdb, rb,gobject
import libdbfm
from DoubanFMSource import DoubanFMSource
import logging,logging.handlers,gtk,gtk.glade
import Setup

log=logging.getLogger('DoubanFM')

channels = {_('私人电台'):0, _('国语歌曲'):1, _('英文歌曲'):2, 
		            _('粤语歌曲'): 6, _('70s'): 3, _('80s'): 4, _('90s'): 5}

class DoubanFM(rb.Plugin):
	
	def __init__(self):
		rb.Plugin.__init__(self)

	def activate(self, shell):
	
		#logging
		log.setLevel(logging.DEBUG)
		console_handler = logging.StreamHandler()
		console_handler.setLevel(logging.DEBUG)
		console_handler.setFormatter(logging.Formatter('%(name)s %(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
		log.addHandler(console_handler)
		self._shell=shell
		self._handler = [
				shell.props.shell_player.connect('playing-song-changed', self._on_playing_song_changed)]
		self.actionGroup=gtk.ActionGroup("DoubanFMActions")
		FavorAction=gtk.Action("Favor",_("喜欢"),_("Trash currently playing track"),"user-trash")
		NoFavorAction=gtk.Action("NoFavor",_("不喜欢"),_("Trash currently playing track"),"user-trash")
		privateAction=gtk.Action("private",_("私人电台"),_("Trash currently playing track"),"user-trash")
		chineseAction=gtk.Action("chinese",_("国语歌曲"),_("Trash currently playing track"),"user-trash")
		englishAction=gtk.Action("english",_("英文歌曲"),_("Trash currently playing track"),"user-trash")
		gongdongAction=gtk.Action("gongdong",_("粤语歌曲"),_("Trash currently playing track"),"user-trash")
		seventyAction=gtk.Action("70s",_("七零年代"),_("Trash currently playing track"),"user-trash")
		eightyAction=gtk.Action("80s",_("八零年代"),_("Trash currently playing track"),"user-trash")
		ninetyAction=gtk.Action("90s",_("九零年代"),_("Trash currently playing track"),"user-trash")
		FavorAction.connect("activate",self.favor,shell)
		NoFavorAction.connect("activate",self.noFavor,shell)
		seventyAction.connect("activate",self.seventyChannel,shell)
		eightyAction.connect("activate",self.eightyChannel,shell)
		ninetyAction.connect("activate",self.ninetyChannel,shell)
		privateAction.connect("activate",self.privateChannel,shell)
		chineseAction.connect("activate",self.chineseChannel,shell)
		englishAction.connect("activate",self.englishChannel,shell)
		gongdongAction.connect("activate",self.gongdongChannel,shell)
		self.actionGroup.add_action(FavorAction)
		self.actionGroup.add_action(NoFavorAction)
		self.actionGroup.add_action(seventyAction)
		self.actionGroup.add_action(eightyAction)
		self.actionGroup.add_action(ninetyAction)
		self.actionGroup.add_action(privateAction)
		self.actionGroup.add_action(chineseAction)
		self.actionGroup.add_action(englishAction)
		self.actionGroup.add_action(gongdongAction)
		
		self._setup=Setup.SetupBox()
		
		self.db = shell.get_property("db")
		self.entry_type = self.db.entry_register_type("DoubanFMEntryType")
			# allow changes which don't do anything
		self.entry_type.can_sync_metadata = True
		self.entry_type.sync_metadata = None
		group = rb.rb_source_group_get_by_name ("stores")
		self.source =gobject.new(DoubanFMSource,
						   shell=shell,
						   entry_type=self.entry_type,
						   plugin=self,
						   source_group=group)
		shell.register_entry_type_for_source(self.source, self.entry_type)
		shell.append_source(self.source, None) 
		self._uiManager=shell.props.ui_manager
		self._uiManager.insert_action_group(self.actionGroup)
		self.uiMergeid=self._uiManager.add_ui_from_file(self.find_file("UI.xml"))
		self._uiManager.ensure_update()

			
   	def seventyChannel(self,action,shell):
		self.source.set_channel(3)
		self.source.resetSongs()
   	def eightyChannel(self,action,shell):
		self.source.set_channel(4)
		self.source.resetSongs()
   	def ninetyChannel(self,action,shell):
		self.source.set_channel(5)
		self.source.resetSongs()
	def privateChannel(self,action,shell):
		self.source.set_channel(0)
		self.source.resetSongs()
   	def chineseChannel(self,action,shell):
		self.source.set_channel(1)
		self.source.resetSongs()
   	def englishChannel(self,action,shell):
		self.source.set_channel(2)
		self.source.resetSongs()
	def gongdongChannel(self,action,shell):
		self.source.set_channel(6)
		self.source.resetSongs()
  
   	def favor(self,action,shell):
            song=self.source.songsMap[self.title.decode("utf-8")]
            log.info('SID:'+song.sid+",AID:"+song.aid);
            self.source.doubanfm.fav_song(song.sid,song.aid)
	def noFavor(self,action,shell):
            song=self.source.songsMap[self.title.decode("utf-8")]
            self.source.doubanfm.unfav_song(song.sid,song.aid)

	def _on_playing_song_changed(self, player, entry):
		self.title=self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
		self.source.__songSize__=self.source.__songSize__-1
		if self.source.__songSize__<1:
			self.source.resetSongs()		
	
	def create_configure_dialog(self):
		self._setup.present()
		return self._setup
	def deactivate(self, shell):
		log.info("deactivate")
		uiManager=shell.get_ui_manager()
		uiManager.remove_ui(self.uiMergeid)
		self.db.entry_delete_by_type(self.entry_type)
		self.db.commit()
		self.db = None
		self.entry_type = None
		self.source.delete_thyself()
		self.source = None
		
