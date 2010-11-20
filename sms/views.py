#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponse
from sms.provider import get_service_provider
import logging
log = logging.getLogger(__name__)

def sms_notification(request, source):
    """A generic event listener for your service providers' notifications.
    Simply, this view will be called by your broker every time a message has
    been received. Service provider should identify itself by passing the
    ``source`` parameter that corresponds with its configuration in
    sms.models.ServiceProviderData.slug."""

    # call provider factory based on slug
    source = source.lower()
    try:
        provider = get_service_provider(slug=source)
    except Exception, e:
        log.critical(e)
        raise Http404()

    # do a simple IP check
    ip = request.META['REMOTE_ADDR']

    if not provider.is_ip_allowed(ip):
        log.warn("Illegal call from %s" % ip)
        raise Http404()

    log.info("Got request notification from %s" % source)

    # extract message data
    try:
        msisdn, text, number = provider.get_primal_data(request.GET)
        log.debug("%s %s %s" % (msisdn, text, number))
    except Exception, e:
        return HttpResponse(provider.handle_notification_error(e, request))

    log.debug("%s Request input: msisdn:%s, text:%s, number:%s" % \
                (source, msisdn, text, number))

    # collect purchase data, send success signal and say thanks to your
    # notification service
    la = provider.get_large_account(la_number = number, text = text)
    provider.dispatch_purchase(la = la, msisdn = msisdn, text = text)
    return HttpResponse(provider.NOTIFICATION_REPLY)

