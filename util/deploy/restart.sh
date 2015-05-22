#!/bin/bash
/etc/init.d/memcached restart
/etc/init.d/celeryd restart
/etc/init.d/celeryd-training restart
/etc/init.d/celerybeat restart
/etc/init.d/httpd restart
