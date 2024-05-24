#!/bin/bash
w3m $(ls -t ~/Documents/rb_data/logs/debug* | head -1 |tail -1)
