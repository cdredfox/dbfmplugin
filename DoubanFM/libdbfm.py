# Copyright (C) 2008-2010 Sun Ning <classicning@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#
# The developers of the Exaile media player hereby grant permission
# for non-GPL compatible GStreamer and Exaile plugins to be used and
# distributed together with GStreamer and Exaile. This permission is
# above and beyond the permissions granted by the GPL license by which
# Exaile is covered. If you modify this code, you may extend this
# exception to your version of the code, but you are not obligated to
# do so. If you do not wish to do so, delete this exception statement
# from your version.


import urllib
import httplib
import json
import re
import random
import contextlib
from Cookie import SimpleCookie

__all__ = ['DoubanFM', 'LoginException', 'DoubanFMChannels']

class LoginException(Exception):
    pass

class DoubanFM(object):
    def __init__ (self, username, password):
        self.uid = None
        self.dbcl2 = None
        self.bid = None
        self._channel = 0
        self.__login__(username, password)
        pass
    
    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    def __login__(self, username, password):
        data = urllib.urlencode({
                'form_email':username, 'form_password':password})
        contentType = "application/x-www-form-urlencoded"
        headers = {"Content-Type":contentType}
        with contextlib.closing(httplib.HTTPConnection("www.douban.com")) as conn:
            conn.request("POST", "/accounts/login", data, headers)
        
            r1 = conn.getresponse()
            resultCookie = SimpleCookie(r1.getheader('Set-Cookie'))

            if not resultCookie.has_key('dbcl2'):
                raise LoginException()

            dbcl2 = resultCookie['dbcl2'].value
            if dbcl2 is not None and len(dbcl2) > 0:
                self.dbcl2 = dbcl2
        
                uid = self.dbcl2.split(':')[0]
                self.uid = uid

            bid = resultCookie['bid'].value
            self.bid = bid
    
    def __format_list__(self, sidlist, verb=None):
        if sidlist is None or len(sidlist) == 0:
            return ''
        else:
            if verb is not None:
                return ''.join(map(lambda s: '|'+str(s)+':'+str(verb), sidlist))
            else:
                return ''.join(map(lambda s: '|'+str(s), sidlist))
                

    def new_playlist(self, history=[]):
        params = self.__get_default_params__('n')
        params['h'] = self.__format_list__(history, True)

        results = self.__remote_fm__(params)

        return json.loads(results)['song']
    
    def __get_default_params__ (self, typename=None):
        params = {}
        for i in ['aid', 'channel', 'du', 'h', 'r', 'rest', 'sid', 'type', 'uid']:
            params[i] = ''

        params['r'] = random.random()
        params['uid'] = self.uid
        params['channel'] = self.channel

        if typename is not None:
            params['type'] = typename

        return params

    
    def __remote_fm__(self, params):
        data = urllib.urlencode(params)
        cookie = 'dbcl2="%s"; bid="%s"' % (self.dbcl2, self.bid)
        header = {"Cookie": cookie}
        with contextlib.closing(httplib.HTTPConnection("douban.fm")) as conn:
            conn.request('GET', "/j/mine/playlist?"+data, None, header)
            result = conn.getresponse().read()

            return result

    def del_song(self, sid, aid, rest=[]):
        params = self.__get_default_params__('b')
        params['sid'] = sid
        params['aid'] = aid
        params['rest'] = self.__format_list__(rest)

        result = self.__remote_fm__(params)
        return json.loads(result)['song']

    def fav_song(self, sid, aid):
        params = self.__get_default_params__('r')
        params['sid'] = sid
        params['aid'] = aid

        self.__remote_fm__(params)
        ## ignore the response

    def unfav_song(self, sid, aid):
        params = self.__get_default_params__('u')
        params['sid'] = sid
        params['aid'] = aid

        self.__remote_fm__(params)

    def skip_song(self, sid, aid, history=[]):
        params = self.__get_default_params__('s')
        params['h'] = self.__format_list__(history[:50])
        params['sid'] = sid
        params['aid'] = aid
    
        result = self.__remote_fm__(params)
        return json.loads(result)['song']

    def played_song(self, sid, aid, du=0):
        params = self.__get_default_params__('e')
        params['sid'] = sid
        params['aid'] = aid
        params['du'] = du

        self.__remote_fm__(params)

    def played_list(self, history=[]):
        params = self.__get_default_params__('p')
        params['h'] = self.__format_list__(history[:50])
        
        results = self.__remote_fm__(params)
        return json.loads(results)['song']

DoubanFMChannels = {'Personalized':0, 'Mandarin':1, 'Western':2,
            'Cantonese': 6, '70s': 3, '80s': 4, '90s': 5}