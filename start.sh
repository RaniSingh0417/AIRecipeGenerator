#!/bin/bash

# Start Rasa server in the background
rasa run --enable-api &

# Start action server
rasa run actions
