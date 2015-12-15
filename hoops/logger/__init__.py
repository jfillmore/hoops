import logging
from logging import Filter, Formatter
import logging.config
import time
import yaml
import traceback
import os

from flask import request

this_dir = os.path.abspath(os.path.dirname(__file__))


def configure_logging(app_name, config_filename=this_dir + '/logging.yaml', log_level='ERROR', log_path='.', logging_config=None):
    """
    Configures the logging according to the setting in the config file and the other parameters
    """
    if type(logging_config) is not dict:
        config_filename = config_filename or this_dir + '/logging.yaml'
        log_level = log_level or 'ERROR'
        log_path = log_path or '.'
        app_name = app_name or 'hoops'

        with open(config_filename) as f:
            cfg_string = f.read()

        # variable substitution
        cfg_string = cfg_string.replace('{log_path}', log_path)
        cfg_string = cfg_string.replace('{app_name}', app_name.replace(' ', '_'))

        logging_config = yaml.load(cfg_string)

    logging.config.dictConfig(logging_config)
    # set global logging level for all the handlers
    disabled_loglevel = max(logging.getLevelName(log_level) - 1, 1)
    logging.disable(disabled_loglevel)


class ContextFilter(Filter):
    """
    This is a filter which injects contextual information into the log.
    """
    def filter(self, record):

        try:
            if request:
                # TODO: Only include this metadata when it is written by the log formatter
                # record.remote_addr = request.remote_addr or 'localhost'
                # record.request_method = request.environ.get('REQUEST_METHOD')
                # record.path_info = request.environ.get('PATH_INFO')
                record.request_uid = request.environ.get('REQUEST_UID', 'request_uid')
            else:
                # record.remote_addr = ''
                # record.request_method = ''
                # record.path_info = ''
                record.request_uid = ''
        except:
            pass

        return True


class UTCFormatter(Formatter):
    """
    This formatter ensures that the log time is UTC, and appends the inner exception message
    """
    converter = time.gmtime

    def formatException(self, exc_info):
        message_array = []
        exc = exc_info[1]
        tb = exc_info[2]
        for line in traceback.format_tb(tb):
            message_array.append(unicode(line))
        # handle inner exception
        try:
            if exc.exception:
                message_array.append(u"  " + unicode(exc.exception))
        except AttributeError:
            pass

        exception_message = u"".join(message_array)

        return exception_message
