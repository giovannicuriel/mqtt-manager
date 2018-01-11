# mqtt-manager

This container bundles mosquitto with mqtt-manager.
Mosquitto is an open source message broker that implements the MQTT protocol.
mqtt-manager provides a REST service to update mosquitto access control list (ACL)
and TLS options easily and 'on the fly'.

## How to build

The recommended way to build mqtt-manager is to build a docker container:

``` bash

docker build -t mqtt-manager .

```

If you'd like to run it by hand, mqtt-manager has the following dependencies
(these packages are related to Ubuntu. Other Linux distributions might have
different names for them):

- python-openssl, python-pip uwsgi-plugin-python,
- nginx
- supervisor

And there are a few other dependencies from pip:

- uwsgi
- flask
- requests
- kafka

There are a few things that must be moved around in order to supervisor, flask
and nginx properly find them. You can check the [dockerfile](https://github.com/dojot/mqtt-manager/blob/master/Dockerfile) to
find out what they are and where do they should go.

## How to run

All mqtt-manager and mosquitto dependencies should be automatically downloaded
and configured when building the container.

If running in standalone mode (without docker and other elements from [dojot's docker-compose](https://github.com/dojot/docker-compose)),
check the [entrypoint](https://github.com/dojot/mqtt-manager/blob/master/entrypoint.sh) script.

Both methods depend on a running instance of [ejbca-rest](http://github.com/dojot/ejbca-rest).

## How to use

A tutorial about how to configure and use mqtt-manager is available [here](./tutorial.html)