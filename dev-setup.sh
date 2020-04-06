#!/bin/bash

[ -z "${REKORDER_VENV}" ] && REKORDER_VENV="$(dirname $0)/venv"

if ! type pip 2>/dev/null && ! type pip3 2>/dev/null
then
  sudo <<!
    apt update
    # Optional: sudo apt upgrade
    apt install python3-pip
    # Other handy stuff
    apt-get install build-essential libssl-dev libffi-dev python-dev
!
fi

if ! type virtualenv
then
  python -m pip install --user virtualenv
fi

if [ ! -d "${REKORDER_VENV}" ]
then
  virtualenv "${REKORDER_VENV}"
  "${REKORDER_VENV}/bin/python" --version
fi

if [ ! -x "${REKORDER_VENV}/bin/rekorder" ]
then
  "${REKORDER_VENV}/bin/pip" install -e .
fi

"${REKORDER_VENV}/bin/rekorder" --help
