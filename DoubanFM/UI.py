#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import urllib
import json
class UI(object):
    
    def buildUIString(self):
        s1="<ui>"
        s1=s1+"<menubar name=\"MenuBar\">"
        s1=s1+"<menu name=\"FMMenu\" action=\"FMMenu\">"
        s1=s1+"<placeholder name=\"DoubanFM\">"
        s1=s1+"<separator/>"
        s1=s1+"<menuitem name=\"Favor\" action=\"Favor\"/>"
        s1=s1+"<menuitem name=\"NoFavor\" action=\"NoFavor\"/>"
        s1=s1+"<menuitem name=\"NeverPlay\" action=\"NeverPlay\"/>"
        s1=s1+"<separator/>"
        menu=""
        channels=self.load_channels()
        for channel in channels['channels']:
            menu=menu+"<menuitem name=\""+'-'.join(channel['name_en'].split('&'))+"\" action=\""+'-'.join(channel['name_en'].split('&'))+"\"/>"
        s1=s1+menu
        s1=s1+"<separator/>"
        s1=s1+"</placeholder>"
        s1=s1+"</menu>"
        s1=s1+"</menubar>"
        s1=s1+"</ui>"
        return s1

    def load_channels(self):
        f=urllib.urlopen("http://www.douban.com/j/app/radio/channels")
        data=f.read()
        f.close()
        channels = json.loads(data)
        return channels
        
        
