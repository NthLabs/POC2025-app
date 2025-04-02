#!/bin/bash

sudo ln -s /home/pocadmin/poc/POC2025-app/bash/etc/nthredirect.service /etc/systemd/system/nthredirect.service
sudo systemctl daemon-reload
sudo systemctl enable nthredirect.service
sudo systemctl start nthredirect.service

sudo chmod 744 /home/pocadmin/poc/POC2025-app/bash/nthredirect.sh

