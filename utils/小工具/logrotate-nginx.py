#!/usr/bin/env python

import datetime, os, sys, shutil

log_path = '/app/nginx/logs/'
log_file = 'www_access.log'

yesterday = (datetime.datetime.now() - datetime.timedelta(days=1))

try:
    os.makedirs(log_path + yesterday.strftime('%Y') + os.sep + \
                yesterday.strftime('%m'))

except OSError as e:
    print(e)
    sys.exit()

shutil.move(log_path + log_file, log_path \
            + yesterday.strftime('%Y') + os.sep \
            + yesterday.strftime('%m') + os.sep \
            + log_file + '_' + yesterday.strftime('%Y%m%d') + '.log')

os.popen("sudo kill -USR1 `cat /app/nginx/logs/nginx.pid`")
