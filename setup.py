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
            'itsdangerous==0.23',
            'Jinja2==2.7.2',
            'FormEncode==1.2.6',
            'Flask==0.10.1',
            'Flask-RESTful==0.2.11',
            'Flask-Babel==0.9',
            'Werkzeug==0.9.4',
            'elementtree==1.2.6-20050316',
            'nose==1.3.0',
            ],
    dependency_links = [
            'git://github.com/rhooper/python-oauth.git#egg=oauth',
            'git://github.com/daaku/python-urlencoding.git#egg=urlencoding',
    ],
    entry_points={
        'console_scripts': [
            'server = run_api:main',
        ],
    }
)
