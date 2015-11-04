#!/bin/bash
find /usr/local/i5k/media/blast/task/ -type d -mtime +15 -exec rm -rf {} \;
