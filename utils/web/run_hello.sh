#!/bin/bash
# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
unset FLASK_APP
unset FLASK_ENV
export FLASK_APP=hello_world.py
#export FLASK_ENV=development
flask run $*
