#!/bin/bash

docker run -d --name bottle-api -p 8080:80 -v $(pwd)/app:/app bottle-api /start-reload.sh
