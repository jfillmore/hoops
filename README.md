hoops!
======
The intention is to make hoops a distributable python module that can be reused by jetlaunch/copper
For that reason, setup.py is used instead of requirements.txt.

An internal pypi server has been set up on http://jenkins.dal5.jetlaunch.co:8001.
It is maintained via the "jenkins" role in jetlaunch-ansible.


### Upload

To be able to package and upload hoops to this server, you need a .pypirc file in your home directory.
This is what mine looks like (you must use the same credentials, upload is protected):

~~~ini
[distutils]
index-servers =
  pypi
  internal
  local

[pypi]
username:jetlaunch
password:*****

[internal]
repository: http://jenkins.dal5.jetlaunch.co:8001
username: jetlaunch
password: matter_you_long

[local]
repository: http://localhost:8080
~~~

To upload, run this from the commandline:

> upload.sh

Upload to a local pypi-server:

> upload.sh local

### Install

To install the hoops package in your local virtualenv:

> pip install --index-url http://jenkins.dal5.jetlaunch.co:8001/simple hoops

or you could create a ~/.pip/pip.conf file:

~~~ini
[global]
extra-index-url = http://jenkins.dal5.jetlaunch.co:8001/simple
~~~

and just run:

> pip install hoops
