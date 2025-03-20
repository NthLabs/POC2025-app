#!/bin/bash

sudo ln -s /home/pocadmin/poc/POC2025-app/bash/etc/nthpoc.service /etc/systemd/system/nthpoc.service
sudo systemctl daemon-reload
sudo systemctl enable nthpoc.service
sudo systemctl start nthpoc.service

sudo chmod 744 /home/pocadmin/poc/POC2025-app/bash/nthpoc.sh

