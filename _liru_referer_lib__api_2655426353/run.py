#-*- mode: python; coding: utf-8 -*-
#
# Copyright 2011 Andrej A Antonov <polymorphm@gmail.com>.
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

assert str is not unicode
assert str is bytes

import glib, gtk

from .main_window import MainWindow

def run(quit):
    main_window = MainWindow(quit)
    
    main_window.present()

def main():
    main_loop = glib.MainLoop()
    
    glib.idle_add(run, main_loop.quit)
    try:
        threads_init = glib.threads_init
    except AttributeError as e:
        try:
            import gtk.gdk
            threads_init = gtk.gdk.threads_init
        except:
            raise e
    threads_init()
    main_loop.run()

