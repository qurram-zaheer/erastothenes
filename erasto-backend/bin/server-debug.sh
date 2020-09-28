#!/bin/bash

export FLASK_APP=./erasto-backend/server.py
export FLASK_ENV=development
export FLASK_DEBUG=1

flask run --port 5000