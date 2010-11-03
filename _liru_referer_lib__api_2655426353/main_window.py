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

import sys, os.path, weakref
import gtk, gtk.gdk

from .task_ctrl import TaskCtrl
from .params_widget import ParamsWidget
from .task_widget import TaskWidget

MAIN_WINDOW_GLADE = os.path.join(
    os.path.dirname(__file__).decode(sys.getfilesystemencoding()),
    'main_window.glade',
)

class MainWindow:
    def __init__(self, quit):
        self.quit = quit
        
        self.task_ctrl = None
        self.params_widget = None
        self.task_widget = None
        self.current_widget = None
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(MAIN_WINDOW_GLADE)
        self.window = self.builder.get_object('main_window')
        
        self.builder.connect_signals(self)
        self.params_widget = ParamsWidget(weakref.ref(self))
        self.set_current_widget(self.params_widget)
        self.window.set_focus(
            self.params_widget.builder.get_object('source_site_entry')
        )
    
    def set_current_widget(self, widget):
        widget_container = self.builder.get_object('main_window_vbox')
        
        if self.current_widget is not None:
            widget_container.remove(self.current_widget.widget)
        
        if widget is not None:
            widget_container.pack_start(widget.widget)
        
        self.current_widget = widget
    
    def present(self):
        self.window.present()
    
    def on_main_window_destroy(self, widget):
        self.quit()
    
    def on_start_action_activate(self, widget):
        if not self.task_ctrl:
            if not self.params_widget.get_source_site():
                hint_widget = self.params_widget.builder.get_object('source_site_entry')
                
                self.window.set_focus(hint_widget)
                gtk.gdk.beep()
                return
            
            if not self.params_widget.get_target_sites_list():
                gtk.gdk.beep()
                return
            
            self.task_ctrl = TaskCtrl()
            
            self.task_widget = TaskWidget(
                weakref.ref(self),
                self.task_ctrl,
                self.params_widget.get_source_site(),
                self.params_widget.get_target_sites_list(),
                self.params_widget.get_limit(),
                self.params_widget.get_workers(),
            )
            
            self.set_current_widget(self.task_widget)
            
            self.task_widget.run()
        else:
            gtk.gdk.beep()
    
    def on_stop_action_activate(self, widget):
        if self.task_ctrl:
            self.task_ctrl.stop()
            self.task_ctrl = None
            self.task_widget = None
            
            self.set_current_widget(self.params_widget)
        else:
            gtk.gdk.beep()

