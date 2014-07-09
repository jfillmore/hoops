from setuptools import setup, find_packages

VERSION = '0.1.0'

setup(
    name='hoops',
    version=VERSION,
    description='Hoops',
    long_description="""Module for REST API common code""",
    namespace_packages = ['hoops'],
    packages=find_packages(exclude=['tests', '*.tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires = [
            'BeautifulSoup==3.2.1',
            'Flask==0.10.1',
            'Flask-Babel==0.9',
            'Flask-Login==0.2.9',
            'Flask-Mail==0.9.0',
            'Flask-RESTful==0.2.11',
            'Flask-SQLAlchemy==1.0',
            'Flask-Script==0.6.6',
            'Jinja2==2.7.2',
            'Mako==0.9.1',
            'Markdown==2.3.1',
            'MarkupSafe==0.18',
            'MySQL-python==1.2.5',
            'Pygments==1.6',
            'SQLAlchemy==0.9.2',
            'Werkzeug==0.9.4',
            'aniso8601==0.82',
            'blinker==1.3',
            'coaster==0.4.0',
            'configobj==4.7.2',
            'coverage==3.7.1',
            'elementtree==1.2.6-20050316',
            'ipdb==0.8',
            'ipython==1.2.0',
            'itsdangerous==0.23',
            'nose==1.3.0',
            'passlib==1.6.2',
            'pytz==2013.9',
            'semantic-version==2.2.2',
            'setuptools-git==1.0',
            'simplejson==3.3.2',
            'six==1.5.2',
            'speaklater==1.3',
            'webassets==0.8',
            'wsgiref==0.1.2',
            'http-parser==0.8.3',
            'restkit==4.2.2',
            'socketpool==0.5.3',
            # FIXME: setup.py does not seem to work with these references.
            # FIXME: I suggest that we switch to different oauth implementation, such as oauthlib
            # '-e git://github.com/rhooper/python-oauth.git#egg=oauth',
            # '-e git://github.com/daaku/python-urlencoding.git#egg=urlencoding',
            ],
    entry_points={
        'console_scripts': [
            'server = run_api:main',
        ],
    }
)
