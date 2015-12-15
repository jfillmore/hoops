#!/usr/bin/env python

import sys


if __name__ == '__main__':
    from hoops.core import create_api
    from models import db
    # imported for auto-route detection
    from todo import views

    db_config = {
        'username': 'root',
        'password': '',
        'hostname': 'localhost',
        'database': 'todo'
    }
    flask_config = {
        'DEBUG': True
    }
    flask_app, db, api = create_api(
        app_name='todo',
        database=db,
        db_config=db_config,
        flask_config=flask_config
    )
    if len(sys.argv) > 1:
        if sys.argv[1] == 'recreate_db':
            from hoops.dbmanager import DBManager
            with flask_app.app_context():
                DBManager(db).recreate_db()
        elif sys.argv[1] == 'run':
            host = '0.0.0.0'
            port = 8888
            if len(sys.argv) > 2:
                host = sys.argv[2]
            if len(sys.argv) > 3:
                port = int(sys.argv[3])
            flask_app.run(host=host, port=port)
        else:
            from flask.ext.script import Manager
            from flask.ext.alembic import ManageMigrations
            manager = Manager(flask_app)
            manager.add_command("migrate", ManageMigrations())
    else:
        sys.stderr.write(
            'Usage: %s recreate_db|run|manage_cmd [ARGS]\n' % (sys.argv[0])
        )
        sys.exit(1)
