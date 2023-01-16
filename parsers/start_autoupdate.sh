#!/bin/bash

watch -n 86400 poetry run python lido_parser.py & watch -n 86400 poetry run python ofac_parser.py