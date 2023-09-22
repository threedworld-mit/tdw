#!/bin/bash

VERSION=$(python3 ./tdw_version.py)

 docker build -t alters/tdw:$VERSION --build-arg TDW_VERSION=$VERSION .