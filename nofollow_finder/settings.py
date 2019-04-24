# coding=utf-8
import logging
import os

from dotenv import load_dotenv


log = logging.getLogger(__name__)


class Settings(object):
    _loaded = False

    def load(self, env_path=None):
        if env_path:
            env_path = self._find_file(env_path.split(','))
        load_dotenv(dotenv_path=env_path)
        self._loaded = True

    def _find_file(self, paths):
        for path in paths:
            if path.startswith('~/'):
                path = '{}{}'.format(os.getenv('HOME'), path[1:])
            if os.path.isfile(path):
                log.debug('Running with settings file: {}'.format(path))
                return path
        log.debug('Running without a settings file.')
        return None

    def __getattr__(self, item):
        if not self._loaded:
            raise RuntimeError('Settings not yet loaded')
        return os.getenv(item)


settings = Settings()
