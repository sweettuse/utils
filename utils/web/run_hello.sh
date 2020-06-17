#!/bin/bash
unset FLASK_APP
unset FLASK_ENV
export FLASK_APP=hello_world.py
#export FLASK_ENV=development
flask run $*
