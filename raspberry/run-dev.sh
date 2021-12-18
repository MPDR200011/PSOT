#!/bin/sh

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

docker run -it --mount type=bind,source="$SCRIPTPATH",target=/scanner --net=host --privileged psot-scanner-dev bash
