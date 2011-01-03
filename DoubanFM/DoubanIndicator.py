#!/usr/bin/env python
#-*- coding: UTF-8 -*-
'''
Created on 2011-1-3

@author: kevin
'''
import appindicator,gtk,DoubanFMSource,logging
log=logging.getLogger('DoubanFM')
class DoubanIndicator(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def indicator(self,shell,source):
        source.ind = appindicator.Indicator ("DoubanFM", "indicator-messages", appindicator.CATEGORY_APPLICATION_STATUS)
        source.ind.set_status (appindicator.STATUS_ACTIVE)
        source.ind.set_attention_icon ("indicator-messages-new")
        source.ind.set_icon("doubanFM")
        # create a menu
        source.menu=gtk.Menu()
        item=gtk.MenuItem("喜欢")
        #if hasattr(source,'currentSong') and source.currentSong.like==1:
        #    item.set_sensitive(False)
        item.connect("activate",source.favor,shell)
        item.show()
        source.menu.append(item)
        item=gtk.MenuItem("取消喜欢")
        item.connect("activate",source.noFavor,shell)
        item.show()
        source.menu.append(item)
        item=gtk.MenuItem("不再播放（垃圾桶）")
        item.connect("activate",source.neverPlay,shell)
        item.show()
        source.menu.append(item)
        #item=gtk.MenuItem("推荐正在播放的歌曲")

        item=gtk.MenuItem("选择电台")
        sub_item=gtk.Menu()
        sub_item.show()
        item.set_submenu(sub_item)
        source.buildSubmenu(sub_item,shell)
        item.show()
        source.menu.append(item)
        source.menu.show()
        
        item=gtk.MenuItem("下一首")
        item.connect("activate",self.next,shell)
        item.show()
        source.menu.append(item)
        
        item=gtk.MenuItem("暂停")
        item.connect("activate",self.pause,shell)
        item.show()
        source.menu.append(item)
        
        source.ind.set_menu(source.menu)  
    
    def next(self,action,shell):
            shell.props.shell_player.do_next()
        
    def pause(self,action,shell):
            shell.props.shell_player.playpause()