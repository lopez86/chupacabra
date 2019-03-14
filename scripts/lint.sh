#!/bin/bash

flake8 --exclude=chupacabra_server/protos/*.py --max-line-length 99 chupacabra_server

# Still need a bunch of work to get options right
mypy --ignore-missing-imports --disallow-incomplete-defs chupacabra_server/.
