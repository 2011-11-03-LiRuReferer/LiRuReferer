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

import functools

class TaskCtrl:
    def __init__(self, parent=None):
        self._is_active = True
        self.parent = parent
    
    def __nonzero__(self):
        """is task activity?"""
        
        if self._is_active:
            if self.parent is not None:
                return bool(self.parent)
            else:
                return True
        else:
            return False
    
    def stop(self):
        """stop activity"""
        
        self._is_active = False
    
    def unstop(self):
        self._is_active = True
    
    def use(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if self:
                return func(*args, **kwargs)
        
        return wrapped

