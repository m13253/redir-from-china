#!/usr/bin/env python

#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2015
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.

import datetime
import email.utils
import itertools
import logging
import os
import random
import re
import sys
import time
import tornado
import tornado.gen
import tornado.httpclient
import tornado.httpserver
import tornado.web

import config


def main():
    tornado.log.enable_pretty_logging()

    listen_address = '127.0.0.1'
    listen_port = 8000
    try:
        if len(sys.argv) == 2:
            listen_port = int(sys.argv[1])
        elif len(sys.argv) == 3:
            listen_address = sys.argv[1]
            listen_port = int(sys.argv[2])
        assert 0 <= listen_port <= 65535
    except (AssertionError, ValueError):
        raise ValueError('port must be a number between 0 and 65535')
    MainHandler.stat = Statistics()
    MainHandler.target = TargetManager()
    BTHandler.message = BTHandler.generate_message()

    application = tornado.web.Application([
        ('/announce', BTHandler),
        ('.*', MainHandler)
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(listen_port, listen_address)
    logging.info('Listening on %s:%s' % (listen_address or '[::]' if ':' not in listen_address else '[%s]' % listen_address, listen_port))
    tornado.ioloop.IOLoop.instance().start()


class MainHandler(tornado.web.RequestHandler):
    def prepare(self):  # Workaround to match all GET/POST/PUT
        self.clear_header('Content-Type')
        self.clear_header('Server')  # Sorry Tornado, but we have to have as less as possible characteristics in our response
        self.set_header('Cache-Control', 'max-age=%d' % config.REDIRECT_CACHE_AGE)
        self.set_header('Expires', email.utils.formatdate(time.time()+config.REDIRECT_CACHE_AGE, usegmt=True))
        self.redirect(self.target.pop(), permanent=False)
        self.stat.push(self.request.host)

    def _handle_request_exception(self, e):
        if not self._finished:
            self.set_status(503)
            self.clear_header('Content-Type')
            self.clear_header('Date')
            self.clear_header('Server')
            self.finish()
        self.log_exception(*sys.exc_info())


class BTHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.clear_header('Server')
        self.set_header('Content-Type', 'text/plain')
        self.set_header('Cache-Control', 'max-age=%d' % config.BT_PROTECT_CACHE_AGE)
        self.set_header('Expires', email.utils.formatdate(time.time()+config.BT_PROTECT_CACHE_AGE , usegmt=True))
        self.finish(self.message)
        MainHandler.stat.push('(BT) '+self.request.host)

    @staticmethod
    def generate_message():
        if isinstance(config.BT_PROTECT_MESSAGE, type(b'')):
            message_bytes = config.BT_PROTECT_MESSAGE
        else:
            message_bytes = config.BT_PROTECT_MESSAGE.encode('utf-8', 'replace')
        interval_bytes = str(config.BT_PROTECT_CACHE_AGE).encode('iso-8859-1', 'replace')
        return b''.join([
            b'd14:failure reason',
            str(len(message_bytes)).encode('iso-8859-1', 'replace'), b':',
            message_bytes,
            b'8:intervali', interval_bytes,
            b'e12:min intervali', interval_bytes, b'ee'
        ])

    def _handle_request_exception(self, e):
        if not self._finished:
            self.set_status(503)
            self.clear_header('Content-Type')
            self.clear_header('Date')
            self.clear_header('Server')
            self.finish()
        self.log_exception(*sys.exc_info())


class TargetManager:
    def __init__(self):
        self.lastpoll = None
        self.targets = list(self.parse_local())
        logging.info('Loaded target.txt for %d items.' % len(self.targets))
        try:
            set_timeout(self.auto_pull, 0, pull_list=config.AUTO_PULL_LIST, pull_interval=config.AUTO_PULL_INTERVAL)
        except AttributeError:
            pass

    def parse_local(self):
        filename = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0] or 'redir.py'))), 'target.txt')
        with open('target.txt', 'r') as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('# Last pull: '):
                    try:
                        self.lastpoll = int(line[13:])
                    except ValueError:
                        logging.warning('Unable to determine the time of last auto pull')
                elif not line.startswith('#'):
                    yield line

    @tornado.gen.engine
    def auto_pull(self, pull_list, pull_interval):
        now = time.time()
        if self.lastpoll is None or self.lastpoll+pull_interval <= now or self.lastpoll > now:
            for sleep_time in fib(5, 8):
                http_client = tornado.httpclient.AsyncHTTPClient()
                try:
                    try:
                        response = yield http_client.fetch(tornado.httpclient.HTTPRequest(pull_list, connect_timeout=60, request_timeout=120, max_redirects=16, user_agent='Mozilla/5.0 Redir-From-China/0.1 (auto update, like Curl) +https://github.com/m13253/redir-from-china'))
                        response.rethrow()
                    except Exception as e:
                        logging.info('Failed when auto pulling: %r, retrying after %d seconds' % (e, sleep_time))
                    body = response.body.decode('utf-8', 'replace')
                    break
                finally:
                    http_client.close()
                yield sleep(sleep_time)
            self.targets = [i for i in re.findall('<a href="([^"]+)"', body) if not (i.startswith('https://b.us7.list-manage.com/') or i.startswith('https://github.com/'))]
            with open('target.txt', 'w') as f:
                f.write('# Last pull: %d\n' % time.time())
                for i in self.targets:
                    f.write(i)
                    f.write('\n')
            logging.info('Auto pulled for %d items.' % len(self.targets))
            set_timeout(self.auto_pull, pull_interval, pull_list=pull_list, pull_interval=pull_interval)
        else:
            set_timeout(self.auto_pull, self.lastpoll+pull_interval-now, pull_list=pull_list, pull_interval=pull_interval)

    def pop(self):
        return random.choice(self.targets)


class Statistics:
    def __init__(self):
        self.last_count = 0
        self.this_count = 0
        self.last_period = {}
        self.this_period = {}
        set_timeout(self.print_stat, config.STATISTICS_INTERVAL)

    def push(self, host):
        self.this_count += 1
        try:
            self.this_period[host] += 1
        except KeyError:
            self.this_period[host] = 1

    def print_stat(self, fout=sys.stderr):
        fout.write('Statistics at %s\n' % time.asctime())
        fout.write('Served %d requests (%+d since last period).\n' % (self.this_count, self.this_count-self.last_count))
        fout.write('Top 10 hosts:\n')
        top_sites = [(v, k) for k, v in self.this_period.items()]
        top_sites.sort(reverse=True)
        del top_sites[1024:]

        for idx, (times, host) in enumerate(itertools.islice(top_sites, 10)):
            fout.write('%3d: %s\t%d requests' % (10-idx, host, times))
            try:
                fout.write(' (%+d)' % (times-self.last_period[host]))
            except KeyError:
                pass
            fout.write('\n')
        fout.write('\n')

        self.last_count = self.this_count
        self.last_period = self.this_period
        #self.this_period = {k: v for v, k in top_sites}
        self.this_period = dict(((k, v) for v, k in top_sites))  # workaround for Python 2.6
        set_timeout(self.print_stat, config.STATISTICS_INTERVAL, fout=fout)


def set_timeout(func, sec, ioloop=None, *args, **kwargs):
    ioloop = ioloop or tornado.ioloop.IOLoop.current()
    if tornado.version_info >= (4,):
        return ioloop.add_timeout(datetime.timedelta(seconds=sec), func, *args, **kwargs)
    else:
        return ioloop.add_timeout(datetime.timedelta(seconds=sec), lambda: func(*args, **kwargs))


@tornado.gen.coroutine
def sleep(sec, ioloop=None):
    ioloop = ioloop or tornado.ioloop.IOLoop.current()
    yield tornado.gen.Task(ioloop.add_timeout, datetime.timedelta(seconds=sec))


def fib(a=0, b=1):
    while True:
        yield a
        a, b = b, a+b


if __name__ == '__main__':
    main()
