from configparser import SafeConfigParser
from base64 import b64decode, urlsafe_b64decode
from codecs import open as codecs_open
from json import loads as json_loads
from os import environ
from os.path import abspath
from os.path import exists
from os.path import join
from os.path import normpath
import logging.config


_project_path = abspath(join(__file__, '..', '..'))
_global_default_conf = normpath(
    join(_project_path, 'cascade_config', 'default.conf'))

try:
    from werkzeug import Href
except ImportError as e:
    def Href(*args, **kwargs):
        raise e


class CascadeConfigParser(SafeConfigParser):

    def gethref(self, section, option):
        """
        This can only be used if werkzeug is installed in this environment.
        It will raise an ImportError otherwise.
        """
        return self._get(section, Href, option)

    def getstr(self, section, option):
        return self._get(section, str, option)

    def getbase64(self, section, option):
        value = self._get(section, str, option)
        return b64decode(value)

    def getjson(self, section, option):
        value = self._get(section, str, option)
        return json_loads(value)

    def geturlsafebase64(self, section, option):
        value = self._get(section, str, option)
        return urlsafe_b64decode(value)

    def getabspath(self, section, option):
        value = self._get(section, str, option)
        return normpath(abspath(join(_project_path, value)))


def custom_config_logging(conf, disable_existing_loggers=True):
    """
    Modified fileConfig from ConfigParser to allow use of
      already parsed conf files.
    """
    formatters = logging.config._create_formatters(conf)

    # critical section
    logging._acquireLock()
    try:
        logging._handlers.clear()
        del logging._handlerList[:]
        # Handlers add themselves to logging._handlers
        handlers = logging.config._install_handlers(conf, formatters)
        logging.config._install_loggers(
            conf, handlers, disable_existing_loggers)
    finally:
        logging._releaseLock()


def load_config(app_name, file_names=()):
    """
    Creates a ConfigParser from configuration files in this order:

    1) default.conf -- default values for cascade_logger loaded from this repo
    2) *args -- any file names passed to this function are loaded
            in the order they are specified
    3) /etc/cascade.conf -- if this file exists, it can be used to
            override configuration on a per-machine basis
    4) /etc/$(app_name).conf -- if this file exists, it can be used to
            override configuration on a per-machine-per-app basis
    5) CASCADE_CONFIG -- colon-separated filenames passed in this environment
            variable will be loaded last as a per-run configuration override

    The first one is automatic, the rest are optional. If all you want is the
    logger settings, then just do load_config('your_app_name') and you're set.
    """
    conf = CascadeConfigParser()

    if not isinstance(app_name, str):
        print(type(app_name))
        raise TypeError('app_name must be a string')

    with codecs_open(_global_default_conf, encoding='utf-8') as f:
        conf.readfp(f, filename=_global_default_conf)
        custom_config_logging(conf)

    app_conf_fn = "/etc/%s.conf" % app_name
    conf_fns = list(file_names) + [app_conf_fn]

    if 'CASCADE_CONFIG' in environ:
        conf_fns.extend(filter(None, environ['CASCADE_CONFIG'].split(':')))

    logger = logging.getLogger('cascade_logger')

    for fn in conf_fns:
        if exists(fn):
            with codecs_open(fn, encoding='utf-8') as f:
                logger.info('loading config: %s', fn)
                conf.readfp(f, filename=fn)
        # else:
        #     logger.info('File Not Found: %s', fn)

    custom_config_logging(conf)
    return conf
