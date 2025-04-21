#!/bin/bash

# Kill any existing Django server processes
pkill -f runserver

# Wait a moment for processes to terminate
sleep 2

# Run the server on port 8001 (instead of default 8000)
python manage.py runserver 8001 