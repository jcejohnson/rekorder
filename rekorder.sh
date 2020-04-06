#!/bin/bash

# TODO: Install if venv/bin/rekorder is missing

self=$(basename $0) ; self=${self/.sh/}

$(dirname $0)/venv/bin/${self} "$@"
