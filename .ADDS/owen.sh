#!/bin/bash

if [ -x /opt/pet/owen/PoC/main.py ] ; then
    /opt/pet/owen/PoC/main.py && /usr/bin/logger -p cron.info "OWEN HTML-file renewed at xx:xx:00 seconds."
    sleep 30
    /opt/pet/owen/PoC/main.py && /usr/bin/logger -p cron.info "OWEN HTML-file renewed at xx:xx:30 seconds."
fi

###########################################################################