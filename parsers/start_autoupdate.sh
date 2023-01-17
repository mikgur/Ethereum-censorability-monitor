#!/bin/bash

watch -n 86400 poetry run python3 lido_parser.py & watch -n 86400 poetry run python3 ofac_parser.py