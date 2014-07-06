#!/usr/bin/env python

# Generic wrapper to start Jetlaunch API servers. By default, the name of the
# script is used to determine which app in 'apps' to import (e.g. the symlinked
# name) (e.g. "ln -s api.py partner.py" => "partner").

import sys
import getopt
import os

def usage():
    msg = '''%s [ARGUMENTS]

ARGUMENTS:

    -a|--app <application>      Application server to run (e.g. partner).
                                Defaults to name of script (e.g. symlink).
    -d|--debug                  Force debug mode.
    -e|--environment <env>      Set which run-time environment to use.
                                Defaults to ENV variable "environment",
                                or "local" if not set.
    -H|--host <ip_address>      Control which IP address to bind to. To bind
                                to all public IPs use "0.0.0.0". Defaults to
                                "127.0.0.1".
    -m|--mock-basekit            Force the mock BaseKit API to be used.
    -p|--port <port>            Specify which port to bind to. The default
                                port is 5000.'''
    print msg % (sys.argv[0])
    sys.exit(2)


def main(argv):
    environment = os.environ.get('environment', 'local')
    # parse out the name of the script we were invoked as, minus the .py extension
    app_name = os.path.basename(sys.argv[0]).rpartition('.py')[0]
    # run-time args will be passed on to Flask
    run_args = {}
    try:
        opts, args = getopt.getopt(argv, 'a:de:mhH:p:', [
            'app=', 'debug', 'environment=', 'mock-basekit', 'help',
            'host=', 'port='
        ])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-a', '--app'):
            app_name = arg
        elif opt in ('-H', '--host'):
            run_args['host'] = arg
        elif opt in ('-d', '--debug'):
            run_args['debug'] = True
        elif opt in ('-p', '--port'):
            run_args['port'] = arg
        elif opt in ('-e', '--environment'):
            environment = arg
        elif opt in ('-m', '--mock-basekit'):
            sys.stderr.write('Enabling mock upstream APIs\n')
            from jetlaunch.consumer import BaseKitAPIClient as BK
            BK.enable_mock_api()

    try:
        (app) = __import__('apps.%s' % app_name, globals(), locals(), ['create_app'], -1)
    except Exception, e:
        sys.stderr.write('Failed to import "create_app" for app "%s":\n%s' % (app_name, e.message))
        sys.exit(1)
    app = app.create_app(environment).run(**run_args)

if __name__ == '__main__':
    main(sys.argv[1:])
