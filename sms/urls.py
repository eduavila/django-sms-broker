#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('sms.views',
    (r'^notification/(?P<source>\w+)', 'sms_notification'),
)
