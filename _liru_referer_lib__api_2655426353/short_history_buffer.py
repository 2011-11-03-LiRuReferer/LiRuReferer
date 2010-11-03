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

class ShortHistoryBuffer:
    def __init__(self, limit):
        self.limit = limit
        self.clean()
    
    def clean(self):
        self._old_history = ''
        self._new_history = ''
        self._value = ''
        self._len = 0
    
    def __len__(self):
        return self._len
    
    def getvalue(self):
        if self._value is None:
            self._value = self._old_history + self._new_history
        
        return self._value
    
    def append(self, value):
        self._value = None
        if self._len < self.limit:
            self._new_history += value
            self._len += 1
        else:
            self._old_history = self._new_history
            self._new_history = value
            self._len = 1

