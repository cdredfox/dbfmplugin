#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import rhythmdb, rb,gobject
import libdbfm
from DoubanFMSource import DoubanFMSource
import logging,logging.handlers,gtk,gtk.glade
import Setup
import appindicator

log=logging.getLogger('DoubanFM')


channels = {'私人电台':'Personalized', '华语歌曲':'Mandarin', '欧美歌曲':'Western', 
		            '粤语歌曲': 'Cantonese', '70s': '70s', '80s': '80s', '90s': '90s','摇滚音乐':'Rock',
		            'NewAge':'NewAge','Fork':'Fork'}

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
		self.actionGroup=gtk.ActionGroup("DoubanFMActions")
		FMMenuAction=gtk.Action("FMMenu",_("豆瓣电台"),_("FMMenu"),"user-trash")
		FavorAction=gtk.Action("Favor",_("喜欢"),_("Favor"),"user-trash")
		NoFavorAction=gtk.Action("NoFavor",_("取消喜欢"),_("NoFavor"),"user-trash")
		neverPlayAction=gtk.Action("NeverPlay",_("不再播放"),_("Never Player"),"user-trash")
		self.actionGroup.add_action(FMMenuAction)
		self.actionGroup.add_action(FavorAction)
		self.actionGroup.add_action(NoFavorAction)
		self.actionGroup.add_action(neverPlayAction)
		for channel in channels.iterkeys():
			sub_item=gtk.MenuItem(channel)
			channelID=libdbfm.DoubanFMChannels.get(channels.get(channel))
			action=gtk.Action(channels.get(channel),channel,_("FM"),"user-trash")
			action.connect("activate",self.changeChannel,shell,channelID)
			self.actionGroup.add_action(action)
		
		
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
		
		group = rb.rb_source_group_get_by_name ("stores")
		self.source =gobject.new(DoubanFMSource,
						   shell=shell,
						   entry_type=self.entry_type,
						   plugin=self,
						   icon=icon,
						   source_group=group)
		shell.register_entry_type_for_source(self.source, self.entry_type)
		shell.append_source(self.source, None) 
		self._uiManager=shell.props.ui_manager
		self._uiManager.insert_action_group(self.actionGroup)
		self.uiMergeid=self._uiManager.add_ui_from_file(self.find_file("UI.xml"))
		self._uiManager.ensure_update()
		self.indicator(shell)

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
	def indicator(self,shell):
		self.ind = appindicator.Indicator ("DoubanFM", "indicator-messages", appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status (appindicator.STATUS_ACTIVE)
		self.ind.set_attention_icon ("indicator-messages-new")
		self.ind.set_icon("doubanFM")
		# create a menu
		self.menu=gtk.Menu()
		item=gtk.MenuItem("喜欢")
		item.connect("activate",self.favor,shell)
		item.show()
		self.menu.append(item)
		item=gtk.MenuItem("取消喜欢")
		item.connect("activate",self.noFavor,shell)
		item.show()
		self.menu.append(item)
		item=gtk.MenuItem("不再播放（垃圾桶）")
		item.connect("activate",self.neverPlay,shell)
		item.show()
		self.menu.append(item)
		#item=gtk.MenuItem("推荐正在播放的歌曲")
		item=gtk.MenuItem("选择电台")
		sub_item=gtk.Menu()
		sub_item.show()
		item.set_submenu(sub_item)
		self.buildSubmenu(sub_item,shell)
		item.show()
		self.menu.append(item)
		self.menu.show()
		self.ind.set_menu(self.menu)
	
	def buildSubmenu(self,item,shell):
		for channel in channels.iterkeys():
			sub_item=gtk.MenuItem(channel)
			channelID=libdbfm.DoubanFMChannels.get(channels.get(channel))
			sub_item.connect("activate",self.changeChannel,shell,channelID)
			sub_item.show()
			item.add(sub_item)