#!/usr/bin/env python

import sys
import os
# note we need the parent directory of this script
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from hoops import create_api
from hoops.test_server import views

api = None
flask = None


if __name__ == '__main__':
    api, flask = create_api(
        flask_conf={'DEBUG': True}
    )

    views.Example.register()
    views.Foo.register()
    views.Bar.register()
