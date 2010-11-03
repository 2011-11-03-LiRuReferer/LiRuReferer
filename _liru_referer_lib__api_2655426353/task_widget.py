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

from .short_history_buffer import ShortHistoryBuffer
from .task_ctrl import TaskCtrl
from .cyclic_list_file import open_cyclic_list
from .task import Task

TASK_WIDGET_GLADE = os.path.join(
    os.path.dirname(__file__).decode(sys.getfilesystemencoding()),
    'task_widget.glade',
)

LOG_BUFFER_SIZE = 100

class TaskWidget:
    def __init__(
                self, main_window_ref,
                general_task_ctrl,
                source_site,
                target_sites_list,
                limit,
                workers,
            ):
        self.main_window_ref = main_window_ref
        self.general_task_ctrl = general_task_ctrl
        self.builder = gtk.Builder()
        self.builder.add_from_file(TASK_WIDGET_GLADE)
        self.widget = self.builder.get_object('widget_alignment')
        
        self._source_site = source_site
        self._target_sites_list = target_sites_list
        self._limit = limit
        
        self.log_buffer = ShortHistoryBuffer(LOG_BUFFER_SIZE)
        
        self.builder.connect_signals(self)
        
        self.builder.get_object('source_site_entry').\
            set_text(source_site.encode('utf-8'))
        self.builder.get_object('target_sites_list_entry').\
            set_text(target_sites_list.encode('utf-8'))
        limit_msg = 'Да, %s' % limit \
            if limit is not None else 'Нет (бесконечно)'
        self.builder.get_object('limit_entry').\
            set_text(limit_msg.encode('utf-8'))
        self.builder.get_object('workers_spinbutton').\
            set_value(workers)
    
    def get_workers(self):
        widget = self.builder.get_object('workers_spinbutton')
        value = widget.get_value_as_int()
        
        return value
    
    def get_workers(self):
        widget = self.builder.get_object('workers_spinbutton')
        value = widget.get_value_as_int()
        
        return value
    
    def get_source_site(self):
        return self._source_site
    
    def get_target_sites_list(self):
        return self._target_sites_list
    
    def get_limit(self):
        return self._limit
    
    def get_workers(self):
        widget = self.builder.get_object('workers_spinbutton')
        value = widget.get_value_as_int()
        
        return value
    
    def on_log_checkbutton_toggled(self, widget):
        visible = widget.get_active()
        low_window = self.builder.get_object('log_scrolledwindow')
        
        if visible:
            log_widget = self.builder.get_object('log_textbuffer')
            log_widget.set_text(self.log_buffer.getvalue().encode('utf-8'))
            low_window.show()
        else:
            low_window.hide()
    
    def clean_log(self):
        self.log_buffer.clean()
        
        widget = self.builder.get_object('log_textbuffer')
        widget.set_text(b'')
    
    def set_log(self, value):
        decor_value = '%s\n%s\n' % (value, '-' * 50)
        self.log_buffer.append(decor_value)
        
        visible = self.builder.get_object('log_checkbutton').get_active()
        if visible:
            widget = self.builder.get_object('log_textbuffer')
            
            if len(self.log_buffer) > 1:
                # обычное наполнение log-виджета (оно быстрее чем постоянная синхронизация с <self.log_buffer>)
                
                end_iter = widget.get_end_iter()
                widget.insert(end_iter, self.log_buffer.getvalue().encode('utf-8'))
            else:
                # чистка log-виджета (чистка путём синхронизации с <self.log_buffer>)
                widget.set_text(self.log_buffer.getvalue().encode('utf-8'))
    
    def set_successes(self, value):
        assert isinstance(value, int)
        widget = self.builder.get_object('successes_entry')
        
        widget.set_text(unicode(value).encode('utf-8'))
    
    def set_errors(self, value):
        assert isinstance(value, int)
        widget = self.builder.get_object('errors_entry')
        
        widget.set_text(unicode(value).encode('utf-8'))
    
    def set_progress(self, value):
        if value < 0:
            value = 0
        elif value > 1:
            value = 1
        
        widget = self.builder.get_object('progressbar')
        
        widget.set_fraction(value)
    
    def clean(self):
        self.set_successes(0)
        self.set_errors(0)
        self.set_progress(0.0)
        self.clean_log()
    
    def on_abort_button_clicked(self, widget):
        widget.set_sensitive(False)
        self.task_ctrl.stop()
        self.set_log('Остановлено аварийно')
    
    def run(self):
        self.clean()
        
        self.task_ctrl = TaskCtrl(self.general_task_ctrl)
        self.builder.get_object('abort_button').set_sensitive(True)
        
        self.task = Task(
            self.task_ctrl,
            self.get_source_site,
            open_cyclic_list(self.get_target_sites_list()),
            self.get_limit,
            self.get_workers,
            set_successes=self.set_successes,
            set_errors=self.set_errors,
            set_log=self.set_log,
            set_progress=self.set_progress,
        )
        
        self.task.run()

