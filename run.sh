#!/usr/bin/env bash
set -e

IMAGE_NAME=optifino_test

docker build -t ${IMAGE_NAME} .
docker run -p 8000:8000 --rm -it ${IMAGE_NAME}
