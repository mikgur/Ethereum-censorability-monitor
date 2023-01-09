#!/bin/bash

echo "Autoupdating of OFAC list is started"

watch -n 86400 ./parse_ofac.sh