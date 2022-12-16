import datetime

from loguru import logger

from flexget import plugin
from flexget.event import event
from flexget.utils.database import Session

logger = logger.bind(name='est_movies_digital_tmdb')


class EstimatesMoviesDigitalTMDB:
    @plugin.priority(2)
    def estimate(self, entry):
        entity_data = {'data_exists': True, 'entity_date': None}
        if 'tmdb_release_dates' in entry:
            logger.verbose('Querying release estimation for {}', entry['title'])
            for release in entry['tmdb_release_dates']:
                if release['type'] == 'digital':
                    entity_data['entity_date'] = entry['tmdb_released']
            return entity_data

        logger.debug(
            'Unable to check release for {}, tmdb_release_dates field is not defined',
            entry['title'],
        )


@event('plugin.register')
def register_plugin():
    plugin.register(
        EstimatesMoviesDigitalTMDB,
        'est_movies_digital_tmdb',
        interfaces=['estimate_release'],
        api_ver=2,
    )
