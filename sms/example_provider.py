#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sms.provider import ServiceProvider
from sms.provider import sms_received
import logging
log = logging.getLogger(__name__)

class DummyProvider(ServiceProvider):
    """Oh hai, I am dummy service provider.

    I don't really know how to send SMS or WAP PUSH, but I can log some messages
    to show you how to implement the required minimum, to make the notification
    workflow complete."""

    def get_primal_data(self, querydict):
        return ( querydict['origin'], \
                 querydict['text'].replace(" ", ".").upper(), \
                 querydict['destination']
                )

    @staticmethod
    def handle_purchase(sender, la, msisdn, extracted_text, *args, **kwargs):
        log.info("Provider DummyProvider caught purchase signal.")
        log.debug((sender, la, msisdn, extracted_text))
        # from now on you should manyally find your content and send
        # appropriate url via wappush or sms

    def send_sms(self, href, msg, msisdn, *args, **kwargs):
        log.debug("Sending SMS: %s %s to %s" % (msg, href, msisdn))

sms_received.connect(DummyProvider.handle_purchase, sender = DummyProvider)
log.debug('handle_purchase is listening.')

