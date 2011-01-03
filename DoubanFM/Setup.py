#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import gtk,gconf,logging,logging.handlers
log=logging.getLogger('DoubanFM')
USER_NAME_KEY='/rhythmbox.plugin.doubanfm.username'
USER_PWD_KEY='/rhythmbox.plugin.doubanfm.userpwd'
ENABLE_INDICATOR='/rhythmbox.plugin.doubanfm.enableindicator'
class SetupBox(gtk.Dialog,object):
	def __init__(self):
		gtk.Dialog.__init__(self,title=_('豆瓣电台插件设置'))
		self._saveButton=gtk.Button('保存')
		self._exitButton=gtk.Button('退出')
		self._userNameLabel = gtk.Label("用户名：")
		self._userPWDLabel = gtk.Label("密  码：")
		self._enableIndicatorCheckBox=gtk.CheckButton("是否启用任务栏图标:")

		self._userNameEntry = gtk.Entry()
   	        self._userNameEntry.set_max_length(50)
		self._userPWDEntry = gtk.Entry()
   	        self._userPWDEntry.set_max_length(50)
		self._userPWDEntry.set_visibility(False)

		try:
			self._userNameEntry.set_text(gconf.client_get_default().get_without_default(USER_NAME_KEY).get_string())	
			self._userPWDEntry.set_text(gconf.client_get_default().get_without_default(USER_PWD_KEY).get_string())
			self._enableIndicatorCheckBox.set_active(gconf.client_get_default().get_without_default(ENABLE_INDICATOR).get_bool())
		except:
			log.warning("取存储的参数出错了，有可能是用户或者密码没有设置")
		self._exitButton.connect('clicked',self.but_Close,None)
		self._saveButton.connect('clicked',self.but_UpdateConfig,None)
		 
		self.vbox.pack_start(self._userNameLabel, True, True, 0)
		self.vbox.pack_start(self._userNameEntry, True, True, 0)
		self.vbox.pack_start(self._userPWDLabel, True, True, 0)
		self.vbox.pack_start(self._userPWDEntry, True, True, 0)
		self.vbox.pack_start(self._enableIndicatorCheckBox,True, True, 0);
		self.action_area.pack_start(self._saveButton, True, True, 0)
		self.action_area.pack_start(self._exitButton, True, True, 0)
		self._userNameLabel.show()
		self._userPWDLabel.show()
  		self._saveButton.show()
		self._exitButton.show()
		self._userNameEntry.show()
		self._userPWDEntry.show()
		self._enableIndicatorCheckBox.show()
		self.set_default_size(300, 100)

	def but_Close(self,widget,data=None):
		self.hide()
		return
	
	def but_UpdateConfig(self,widget,data=None):
		userName=self._userNameEntry.get_text()
		userPWD=self._userPWDEntry.get_text()
		enableIndicator=self._enableIndicatorCheckBox.get_active()
		gconf.client_get_default().set_string(USER_NAME_KEY,userName)
		gconf.client_get_default().set_string(USER_PWD_KEY,userPWD)
		gconf.client_get_default().set_bool(ENABLE_INDICATOR,enableIndicator)
		self.hide()
		return
		
		
