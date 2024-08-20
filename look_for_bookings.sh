#!/bin/bash

echo "------------------------------------------------------------"
echo "Starting the script for looking for bookings at $(date)"
which python3

source /home/debian/apps/100jours/100-jours/bin/activate
which python3

python3 /home/debian/apps/100jours/priere_non_stop.py
