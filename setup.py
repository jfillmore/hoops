from setuptools import setup, find_packages

VERSION = '0.1.0'

setup(
    name='hoops',
    version=VERSION,
    description='RESTFul API engine',
    long_description="""Module for creating and managing RESTful APIs using a declarative syntax.""",
    namespace_packages=['hoops'],
    packages=find_packages(exclude=['tests', '*.tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'itsdangerous==0.23',
        'argparse==1.2.1',
        'Babel==1.3',
        'Jinja2==2.7.2',
        'FormEncode==1.2.6',
        'Flask==0.10.1',
        'Flask-RESTful==0.2.11',
        'Flask-Babel==0.9',
        'Flask-SQLAlchemy==1.0',
        'MySQL-python==1.2.5',
        'SQLAlchemy==0.9.7',
        'Werkzeug==0.9.4',
        'configobj==5.0.5',
        'coaster==0.4.2',
        'configure==0.5',
        'simplejson==3.6.2',
        'passlib==1.6.2',
        'PyYAML==3.11',
        'python-logstash==0.4.2',
        'logstash-formatter==0.5.8',
    ],
    dependency_links=[
        'git://github.com/rhooper/python-oauth.git#egg=oauth',
        'git://github.com/daaku/python-urlencoding.git#egg=urlencoding',
    ],
    entry_points={
        'console_scripts': [
            'server = run_api:main',
        ],
    },
    scripts=[
        'scripts/api.py'
    ]
)
