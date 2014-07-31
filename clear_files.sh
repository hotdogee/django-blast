#!/bin/bash
find /usr/local/i5k/media/ -type d -mtime +15 -exec rm -rf {} \;
