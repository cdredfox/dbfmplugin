#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import rhythmdb, rb,gobject
import libdbfm
from DoubanFMSource import DoubanFMSource
import logging,logging.handlers,gtk,gtk.glade
import Setup,gconf
import DoubanIndicator
import UI

log=logging.getLogger('DoubanFM')


class DoubanFMEntryType(rhythmdb.EntryType):
	def __init__(self):
		rhythmdb.EntryType.__init__(self,name="DoubanFMEntryType")
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
		self._ui=UI.UI();
		self.build_actions()
		self._setup=Setup.SetupBox()
		
		self.db = shell.get_property("db")
		try:
			self.entry_type = DoubanFMEntryType()
			self.db.register_entry_type(self.entry_type)
		except NotImplementedError:
			self.entry_type = self.db.entry_register_type("DoubanFMEntryType")
			# allow changes which don't do anything
		self.entry_type.can_sync_metadata = True
		self.entry_type.sync_metadata = None
		
		theme = gtk.icon_theme_get_default()
	
		width, height = gtk.icon_size_lookup(gtk.ICON_SIZE_LARGE_TOOLBAR)
		icon = rb.try_load_icon(theme, "doubanFM", width, 0)
		
		#group = rb.rb_source_group_get_by_name ("stores")
		group = rb.rb_display_page_group_get_by_id ("stores")
		self.source =gobject.new(DoubanFMSource,
						   shell=shell,
						   entry_type=self.entry_type,
						   pixbuf=icon,
						   plugin=self)				   
		shell.register_entry_type_for_source(self.source, self.entry_type)
		shell.append_display_page(self.source, group)
		#shell.append_source(self.source, None) 
		self._uiManager=shell.props.ui_manager
		self._uiManager.insert_action_group(self.actionGroup)
		# self.uiMergeid=self._uiManager.add_ui_from_file(self.find_file("UI.xml"))
		#生成界面
		log.info(self._ui.buildUIString())
		self.uiMergeid=self._uiManager.add_ui_from_string(self._ui.buildUIString())
		self._uiManager.ensure_update()
		if gconf.client_get_default().get_without_default(Setup.ENABLE_INDICATOR).get_bool():
			doubanIndicator=DoubanIndicator.DoubanIndicator()
			doubanIndicator.indicator(shell,self)

	def neverPlay(self,action,shell):
		song=self.source.songsMap[self.title.decode("utf-8")]
		self.source.doubanfm.del_song(song.sid,song.aid)
		shell.props.shell_player.do_next()
	
	def changeChannel(self,action,shell,channel):
		self.source.set_channel(channel)
		self.source.resetSongs()
		
   	def favor(self,action,shell):
   		song=self.source.songsMap[self.title.decode("utf-8")]
   		log.info('SID:'+song.sid+",AID:"+song.aid);
   		self.source.doubanfm.fav_song(song.sid,song.aid)
	def noFavor(self,action,shell):
		song=self.source.songsMap[self.title.decode("utf-8")]
		self.source.doubanfm.unfav_song(song.sid,song.aid)
		shell.props.shell_player.do_next()
	def _on_playing_song_changed(self, player, entry):
		self.title=self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
		self.currentSong=self.source.songsMap[self.title.decode("utf-8")]
		log.info(self.currentSong.title)
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
		#self.db.entry_delete_by_type(self.entry_type)
		self.db.commit()
		self.db = None
		self.entry_type = None
		self.source.delete_thyself()
		self.source = None
	
	def buildSubmenu(self,item,shell):
		channels=self._ui.load_channels()
		for channel in channels['channels']:
			sub_item=gtk.MenuItem(channel['name'])
			sub_item.connect("activate",self.changeChannel,self._shell,channel['channel_id'])
			sub_item.show()
			item.add(sub_item)
	
	def build_actions(self):
		self.actionGroup=gtk.ActionGroup("DoubanFMActions")
		FMMenuAction=gtk.Action("FMMenu",_("豆瓣电台"),_("FMMenu"),"user-trash")
		FavorAction=gtk.Action("Favor",_("喜欢"),_("Favor"),"user-trash")
		NoFavorAction=gtk.Action("NoFavor",_("取消喜欢"),_("NoFavor"),"user-trash")
		neverPlayAction=gtk.Action("NeverPlay",_("不再播放"),_("Never Player"),"user-trash")
		self.actionGroup.add_action(FMMenuAction)
		self.actionGroup.add_action(FavorAction)
		self.actionGroup.add_action(NoFavorAction)
		self.actionGroup.add_action(neverPlayAction)
		
		channels=self._ui.load_channels()
		for channel in channels['channels']:
			sub_item=gtk.MenuItem(channel['name'])
			action=gtk.Action('-'.join(channel['name_en'].split("&")),channel['name'],("FM"),"user-trash")
			action.connect("activate",self.changeChannel,self._shell,channel['channel_id'])
			self.actionGroup.add_action(action)		
