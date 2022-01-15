#!/bin/sh

set -x

docker buildx build . --tag mpdr/psot-scanner:latest --push
