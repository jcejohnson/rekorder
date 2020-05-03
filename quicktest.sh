#!/bin/bash

set -e

./dev-setup.sh

rm -rf examples/rekorder
git clone --depth=1 git@github.com:jcejohnson/rekorder.git examples/rekorder
(cd examples/rekorder ; git fetch --tags)  # ex005 tests against v0.1.0

for i in $(seq 1 6)
do
  echo "============================================================"
  echo "Execute: examples/ex00${i}.py"
  examples/ex00${i}.py
  echo "Validate: examples/ex00${i}.py"
  ./rekorder.sh playback --input ex00${i}.json 2>&1 | tee tmp/ex00${i}.log
  echo
done
