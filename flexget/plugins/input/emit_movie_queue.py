from __future__ import unicode_literals, division, absolute_import
import logging
from datetime import datetime

from flexget.entry import Entry
from flexget.plugin import register_plugin, get_plugin_by_name, DependencyError
from flexget.utils.imdb import make_url as make_imdb_url
from flexget.utils.tools import parse_timedelta

try:
    from flexget.plugins.filter.movie_queue import queue_get
except ImportError:
    raise DependencyError(issued_by='emit_movie_queue', missing='movie_queue')

log = logging.getLogger('emit_movie_queue')


class EmitMovieQueue(object):
    """Use your movie queue as an input by emitting the content of it"""

    def validator(self):
        from flexget import validator
        root = validator.factory()
        root.accept('boolean')
        advanced = root.accept('dict')
        advanced.accept('boolean', key='year')
        advanced.accept('boolean', key='quality')
        advanced.accept('interval', key='try_every')
        return root

    def prepare_config(self, config):
        if isinstance(config, bool):
            config = {}
        config.setdefault('year', True)
        config.setdefault('quality', False)
        config.setdefault('try_every', '0 seconds')
        return config

    def on_task_input(self, task, config):
        if not config:
            return
        config = self.prepare_config(config)
        max_last_emit = datetime.utcnow() - parse_timedelta(config['try_every'])

        entries = []

        for queue_item in queue_get(session=task.session):
            if queue_item.last_emit and queue_item.last_emit > max_last_emit:
                log.debug('Waiting to emit %s', queue_item.title)
                continue
            queue_item.last_emit = datetime.utcnow()
            entry = Entry()
            # make sure the entry has IMDB fields filled
            entry['url'] = ''
            if queue_item.imdb_id:
                entry['imdb_url'] = make_imdb_url(queue_item.imdb_id)
                entry['imdb_id'] = queue_item.imdb_id
            if queue_item.tmdb_id:
                entry['tmdb_id'] = queue_item.tmdb_id

            get_plugin_by_name('tmdb_lookup').instance.lookup(entry)
            # check if title is a imdb url (leftovers from old database?)
            # TODO: maybe this should be fixed at the queue_get ...
            if 'http://' in queue_item.title:
                log.debug('queue contains url instead of title')
                if entry.get('movie_name'):
                    entry['title'] = entry['movie_name']
                else:
                    log.error('Found imdb url in imdb queue, but lookup failed: %s' % entry['title'])
                    continue
            else:
                # normal title
                entry['title'] = queue_item.title

            # Add the year and quality if configured to
            if config.get('year') and entry.get('movie_year'):
                entry['title'] += ' %s' % entry['movie_year']
            # TODO: qualities can now be ranges.. how should we handle this?
            if config.get('quality') and queue_item.quality != 'ANY':
                log.info('quality option of emit_movie_queue is disabled while we figure out how to handle ranges')
                #entry['title'] += ' %s' % queue_item.quality
            entries.append(entry)
            log.debug('Added title and IMDB id to new entry: %s - %s' %
                     (entry['title'], entry['imdb_id']))

        return entries

register_plugin(EmitMovieQueue, 'emit_movie_queue', api_ver=2)
