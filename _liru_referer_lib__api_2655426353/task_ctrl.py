#-*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without_path even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function, unicode_literals

import weakref, functools

import glib

class TaskCtrl:
    def __init__(self, parent=None):
        self.immediate_stop_handlers = {}
        self.stop_handlers = {}
        
        if parent is not None:
            self.parent_ref = weakref.ref(parent)
            self._is_active = bool(parent)
            parent.connect('immediate_stop', self._parent_stop_handler)
        else:
            self.parent_ref = None
            self._is_active = True
    
    def connect(self, event_name, handler, *args):
        handler_id = object()
        
        if event_name == 'immediate_stop':
            self.immediate_stop_handlers[handler_id] = handler, args
        elif event_name == 'stop':
            self.stop_handlers[handler_id] = handler, args
        else:
            raise NotImplementedError()
        
        return handler_id
    
    def disconnect(self, event_name, handler_id):
        if event_name == 'immediate_stop':
            del self.immediate_stop_handlers[handler_id]
        elif event_name == 'stop':
            del self.stop_handlers[handler_id]
        else:
            raise NotImplementedError() 
    
    def __nonzero__(self):
        """is task activity?"""
        
        return self._is_active
    
    def stop(self):
        """stop activity"""
        
        self._is_active = False
        
        for handler, args in self.immediate_stop_handlers.values():
            handler(self, *args)
        
        for handler, args in self.stop_handlers.values():
            glib.idle_add(handler, self, *args)
    
    def _parent_stop_handler(self, sender):
        if not self:
            self.stop()
    
    def unstop(self):
        self._is_active = True
    
    def use(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if self:
                return func(*args, **kwargs)
        
        return wrapped

