#!/bin/bash

if [ -x /opt/pet/owen/main.py ] ; then
    /opt/pet/owen/main.py && /usr/bin/logger -p cron.info "OWEN HTML-file renewed at xx:xx:00 seconds."
    sleep 30
    /opt/pet/owen/main.py && /usr/bin/logger -p cron.info "OWEN HTML-file renewed at xx:xx:30 seconds."
fi

###########################################################################