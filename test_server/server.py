#!/usr/bin/env python

import sys
import os
from os.path import expanduser

# note we need the parent directory of this script
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from hoops import create_api, load_config_file
from hoops.test_server import views

config_file = expanduser('~') + '/.hoops_db.yml'
config = load_config_file(config_file, 'local')

api = None
flask = None


if __name__ == '__main__':
    api, flask = create_api(
        config_file=config_file,
        db_conf=config,
        flask_conf={'DEBUG': True},
        app_name='hoops',
    )

    views.Example.register()
    views.Foo.register()
    views.Bar.register()
