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

import sys, os.path
import gtk

from .task_ctrl import TaskCtrl

PARAMS_WIDGET_GLADE = os.path.join(
    os.path.dirname(__file__).decode(sys.getfilesystemencoding()),
    'params_widget.glade',
)

class ParamsWidget:
    def __init__(self, main_window_ref):
        self.main_window_ref = main_window_ref
        self.builder = gtk.Builder()
        self.builder.add_from_file(PARAMS_WIDGET_GLADE)
        self.widget = self.builder.get_object('widget_alignment')
        
        self.builder.connect_signals(self)
        
        self.set_source_site('http://www.example.org/')
        self.set_limit_value(500)
        self.set_workers(10)
    
    def get_source_site(self):
        widget = self.builder.get_object('source_site_entry')
        value = widget.get_text().decode('utf-8').strip()
        
        return value
    
    def set_source_site(self, value):
        widget = self.builder.get_object('source_site_entry')
        widget.set_text(value.encode('utf-8'))
    
    def get_target_sites_list(self):
        widget = self.builder.get_object('target_sites_list_filechooserbutton')
        bytes_value = widget.get_filename()
        
        value = bytes_value.decode('utf-8') \
            if bytes_value is not None else None
        
        return value
    
    def get_use_limit(self):
        widget = self.builder.get_object('limit_checkbutton')
        value = widget.get_active()
        return value
    
    def set_use_limit(self, value):
        widget = self.builder.get_object('limit_checkbutton')
        spinbutton = self.builder.get_object('limit_spinbutton')
        
        widget.set_active(value)
    
    def on_limit_checkbutton_toggled(self, widget):
        spinbutton = self.builder.get_object('limit_spinbutton')
        
        if widget.get_active():
            spinbutton.set_sensitive(True)
        else:
            spinbutton.set_sensitive(False)
    
    def get_limit_value(self):
        widget = self.builder.get_object('limit_spinbutton')
        value = widget.get_value_as_int()
        return value
    
    def set_limit_value(self, value):
        widget = self.builder.get_object('limit_spinbutton')
        widget.set_value(value)
    
    def get_limit(self):
        if self.get_use_limit():
            return self.get_limit_value()
    
    def set_limit(self, value):
        if not self.use_limit:
            self.set_use_limit(True)
        
        self.set_limit_value(value)
    
    def get_workers(self):
        widget = self.builder.get_object('workers_spinbutton')
        value = widget.get_value_as_int()
        return value
    
    def set_workers(self, value):
        widget = self.builder.get_object('workers_spinbutton')
        widget.set_value(value)

