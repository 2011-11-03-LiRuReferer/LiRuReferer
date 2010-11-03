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

import contextlib, random, urllib, urllib2

import glib

from .glib_threading import idle_add_thread

REQUEST_TIMEOUT = 10.0

class StopTask(Exception):
    pass

class NotGoodResultError(IOError):
    pass

def fix_url(site):
    if site.startswith('http:') or \
            site.startswith('https:'):
        return site
    else:
        return 'http://%s' % site

class Task:
    def __init__(
                self,
                task_ctrl,
                get_source_site,
                get_target_site,
                get_limit,
                get_workers,
                set_successes=None,
                set_errors=None,
                set_log=None,
                set_progress=None,
            ):
        self.task_ctrl = task_ctrl
        self.get_source_site = get_source_site
        self.get_target_site = get_target_site
        self.get_limit = get_limit
        self.get_workers = get_workers
        self.set_successes = set_successes
        self.set_errors = set_errors
        self.set_log = set_log
        self.set_progress = set_progress
        
        self.req_id = 0 # переменная для генерации номеров запросов
        
        self.site_pair_successes = {} # успехов индивидуально для каждой из пар источник+цель
        self.all_successes = 0 # всего успехов при запросах
        self.all_errors = 0 # всего ошибок при запросах
        self.all_site_pairs = set() # всего уникальных пар источник+цель
        self.done_criterion = 0 # критерий того что возможно всё что надо уже обработано
        
        self.used_workers = 0 # задействованно "Рабочих"
        self.last_progress = 0.0 # последнее значение прогресса
    
    def show_error(self, e):
        if isinstance(e, StopTask):
            self.set_log(unicode(e))
        else:
            self.set_log(
                'Произошла ошибка обработчика задания. Деятельность остановлена\n\n'
                'Подробности:\n%s\n%s'
                % (
                    unicode(e), type(e)
                )
            )
    
    def update_progress(self):
        # расчитываем прогресс как -- 
        #       число успехов делённое
        #       на число обнаруженных уникальных пар помноженных на лимит
        
        limit = self.get_limit()
        uniq_pairs = len(self.all_site_pairs)
        
        if limit is not None and uniq_pairs:
            progress = self.all_successes / (uniq_pairs * limit)
            
            self.set_progress(progress)
    
    def idle(self):
        try:
            try:
                source_site = fix_url(self.get_source_site())
                target_site = fix_url(self.get_target_site())
                limit = self.get_limit()
                workers = self.get_workers()
            except Exception as e:
                raise StopTask(
                    'Ошибка при получении информации для задания\n\nПодробности:\n%s\n%s' % (
                        unicode(e), type(e)
                    )
                )
            
            site_pair = (source_site, target_site)
            if site_pair not in self.all_site_pairs:
                self.all_site_pairs.add(site_pair)
            uniq_pairs = len(self.all_site_pairs)
            
            if limit is not None:
                # ещё не конец?
                
                if self.site_pair_successes.get(site_pair, 0) >= limit:
                    # пропускаем обработку этой пары источник+цель, и увеличиваем "критерий конца"
                    self.done_criterion += 1
                    
                    if self.done_criterion >= uniq_pairs:
                        # да! это конец
                        
                        self.task_ctrl.stop()
                        self.set_log('Готово!')
                        self.set_progress(1.0)
                        
                        return
                    else:
                        # запустим меня ещё раз! (чтобы я обработал другие данные)
                        #   а вот "нанимать рабочих" с такими данными не надо
                        return True
                else:
                    # сбрасываем "критерий конца"..
                    self.done_criterion = 0
            
            if self.used_workers < workers:
                # есть свободные рабочии.. значит можем запустить деятельность запроса
                
                req_id = self.req_id
                self.req_id += 1
                
                self.set_log(
                    'Начат запрос [%s]: %s -> %s...' % (
                        req_id, repr(source_site), repr(target_site)
                    )
                )
                
                self.used_workers += 1
                
                idle_add_thread(
                    self.task_ctrl.use(self.thread_target),
                    args=[req_id, source_site, target_site]
                )
                
                if self.used_workers < workers:
                    # свободные рабочие есть ЕЩЁ! запустим меня ещё раз!
                    return True
        except Exception as e:
            self.task_ctrl.stop()
            self.show_error(e)
    
    def finally_idle(self, req_id, source_site, target_site, error):
        try:
            if error is None:
                site_pair = (source_site, target_site)
                
                self.site_pair_successes[site_pair] = \
                    self.site_pair_successes.get(site_pair, 0) + 1
                self.all_successes += 1
                
                self.set_successes(self.all_successes)
                self.set_log(
                    'Готов запрос [%s]: %s -> %s (Успех)' % (
                        req_id, repr(source_site), repr(target_site)
                    )
                )
                self.update_progress()
            else:
                self.all_errors += 1
                
                self.set_errors(self.all_errors)
                self.set_log(
                    'Ошибка запроса [%s]: %s -> %s\n\nПодробности:\n%s\n%s' % (
                        req_id,
                        repr(source_site), repr(target_site),
                        unicode(error), type(error)
                    )
                )
            
            self.used_workers -= 1
            
            glib.idle_add(self.task_ctrl.use(self.idle))
        except Exception as e:
            self.task_ctrl.stop()
            self.show_error(e)
    
    def thread_target(self, req_id, source_site, target_site):
        try:
            referer = source_site
            site = target_site
            counter_url = 'http://counter.yadro.ru/hit?t13.2;r%(referer)s;s1280*1024*24;u%(site)s;%(random)s' % {
                'referer': urllib.quote(referer),
                'site': urllib.quote(site),
                'random': random.random(),
            }
            
            timeout=10.0
            
            opener = urllib2.build_opener()
            opener.addheaders = [
                (b'Accept', b'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                (b'Accept-Charset', b'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
                (b'Accept-Language', b'ru,en-gb;q=0.8,en-us;q=0.5,en;q=0.3'),
                (b'Connection', b'keep-alive'),
                (b'Keep-Alive', b'115'),
                (b'Referer', site.encode('utf-8')),
                (
                    b'User-Agent',
                    b'Mozilla/5.0 (X11; U; Linux x86_64; ru; rv:1.9.1.1; f/%s) Gecko/20090730.%s Gentoo Firefox/3.5.1.%s %s/%s' % (
                        random.random(), random.random(), random.random(), random.random(), random.random()
                    )
                ),
            ]
            
            body_start_sample = b'GIF89aX\x00'
            
            with contextlib.closing(
                opener.open(counter_url, timeout=REQUEST_TIMEOUT)
            ) as req:
                code = req.getcode()
                body_start = req.read(len(body_start_sample))
            
            if code != 200:
                raise NotGoodResultError('Код ответа не равен 200')
            if body_start != body_start_sample:
                raise NotGoodResultError('Ответ не выглядет как GIF-картинка')
        except Exception as e:
            error = e
        else:
            error = None
        
        glib.idle_add(self.task_ctrl.use(self.finally_idle), req_id, source_site, target_site, error)
    
    def run(self):
        glib.idle_add(self.task_ctrl.use(self.idle))

