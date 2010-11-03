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

import glib, threading

def _idle_add_thread_callback(target, name, args, kwargs):
    if args is None:
        args = []
    
    if kwargs is None:
        kwargs = {}
    
    thread = threading.Thread(
        target=target, name=name,
        args=args, kwargs=kwargs
    )
    thread.daemon = True
    thread.start()

def idle_add_thread(
            target,
            name=None, args=None, kwargs=None,
            priority=None):
    if priority is None:
        priority = glib.PRIORITY_DEFAULT_IDLE
    
    idle_id = glib.idle_add(
        _idle_add_thread_callback,
        target, name, args, kwargs,
        priority=priority,
    )
    
    return idle_id

