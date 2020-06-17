#!/bin/bash
# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
unset FLASK_APP
unset FLASK_ENV
export FLASK_APP=tusebot.py
#export FLASK_ENV=development
flask run $*
