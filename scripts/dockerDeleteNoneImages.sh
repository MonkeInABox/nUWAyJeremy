#!/bin/bash

docker image remove $(docker images | grep none | awk '{ print $3 }')