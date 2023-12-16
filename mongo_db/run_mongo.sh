#!/bin/bash

NETWORK_NAME="neutrality_watch_network"

# Check if the network exists
if [ -z "$(docker network ls | grep $NETWORK_NAME)" ]; then
  echo "Network $NETWORK_NAME does not exist, creating..."
  docker network create $NETWORK_NAME
else
  echo "Network $NETWORK_NAME already exists, connecting..."
fi

# Now run docker-compose
docker compose up --detach