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

class FileZeroError(IOError):
    pass

def open_cyclic_list_iter(filename):
    while True:
        zero = True
        with open(filename, 'rb') as fd:
            for raw_line in fd:
                line = raw_line.decode('utf-8', 'replace').strip()
                
                if line:
                    yield line
                    zero = False
        if zero:
            raise FileZeroError('File is zero: %s' % repr(filename))

def open_cyclic_list(filename):
    generator = open_cyclic_list_iter(filename)
    
    def get_next():
        return next(generator)
    
    return get_next

