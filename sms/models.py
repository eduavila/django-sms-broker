#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class ServiceProviderData(models.Model):
    """(ServiceProvider description)"""

    date_created = models.DateTimeField(blank = False, auto_now_add = True, \
                    editable = False)
    date_changed = models.DateTimeField(blank = False, auto_now = True, \
                    editable = False)
    name = models.CharField(max_length = 255)
    slug = models.SlugField(unique = True)
    module = models.CharField(max_length = 255)

    class Meta:
        verbose_name = "ServiceProvider"
        verbose_name_plural = "ServiceProviders"

    def __unicode__(self):
        return u"%s" % self.name

class Prefix(models.Model):
    """(Prefix description)"""

    date_created = models.DateTimeField(blank = False, auto_now_add = True, \
                    editable = False)
    date_changed = models.DateTimeField(blank = False, auto_now = True, \
                    editable = False)
    value = models.CharField(blank = False, max_length = 64, unique = True)

    class Meta:
        verbose_name = "Prefix"
        verbose_name_plural = "Prefixes"

    def __unicode__(self):
        return u"%s" % self.value

class LargeAccount(models.Model):
    """(LargeAccount description)"""

    date_created = models.DateTimeField(blank = False, auto_now_add = True, \
                    editable = False)
    date_changed = models.DateTimeField(blank = False, auto_now = True, \
                    editable = False)
    number = models.PositiveIntegerField(blank = False, null = False)
    prefixes = models.ManyToManyField(Prefix)
    provider = models.ForeignKey(ServiceProviderData)

    class Meta:
        verbose_name = "LargeAccount"
        verbose_name_plural = "LargeAccounts"

    def __unicode__(self):
        return u"LA %s (%s)" % (self.number, self.provider)

from sms.provider import sms_received
