#!/bin/sh

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

docker run -it --mount type=bind,source="$SCRIPTPATH",target=/app --net=host --privileged psot-aggregator-dev bash
