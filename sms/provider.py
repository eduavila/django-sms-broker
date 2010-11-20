#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sms.models import ServiceProviderData, LargeAccount
import django.dispatch
import logging
log = logging.getLogger(__name__)

sms_received = django.dispatch.Signal(providing_args = ['la', 'msisdn', 'extracted_text'])

class MethodNotImplemented(Exception): pass

class ServiceProvider(object):
    """ServiceProvider is meant to be subclassed.
    To keep the interface a bit more readable, methods that *have* to be
    overriden (in order to use them, note that some are in fact optional), are
    raising MethodNotImplemented exception.

    ServiceProvider object represents real-world SMS broker instance, being
    able to send WAP/SMS via any kind of interface (most of the time you
    will probably deal with simple REST webservice).
    """

    NOTIFICATION_REPLY = u"OK"
    ERROR_REPLY = u"ERR"

    def __init__(self, db_id = None, *args, **kwargs):
        self.db_id = int(db_id)
        log.debug("Instantiating service provider %s" % db_id)
        super(ServiceProvider, self).__init__(*args, **kwargs)

    def send_wap_push(self, href, msg, msisdn, *args, **kwargs):
        """Implementation of this method is optional, since you may want just to
        receive notifications regarding SMS events and not sendning any text
        messages by yourself.
        The usual implementation is your broker's webservice call.

        Please do remember, that WAP PUSH messages are not handled equally by
        all handsets. Therefore you should either let your users choose wheter
        they want to receieve SMS / WAP PUSH messages, or detect appropriate
        handset by yourself. If you need an idea on how to detect handsets,
        please head to following third parties:

            - http://deviceatlas.com/
            - http://wurfl.sourceforge.net/
        """

        raise MethodNotImplemented('Override send_wap_push')

    def send_sms(self, href, msg, msisdn, *args, **kwargs):
        """See send_wap_push() documentation."""

        raise MethodNotImplemented('Override send_wap_push')

    def is_ip_allowed(self, ip):
        """Simple security check may be performed here if you would like to make
        sure that no external party is sending you event notifications."""

        log.warn("%s.is_ip_allowed not implemented. Returning True for %s." % \
            (self.__class__, ip))
        return True

    def get_primal_data(self, querydict):
        """This method should return (msisdn, text, number) tuple, where msisdn
        is the user device number, text is the message content and number
        usually identifies broker's Large Account number. Please note, that a
        full copy of request object querydict will be passed to this function."""

        raise MethodNotImplemented('Override %s.get_primal_data' % \
                                    self.__class__)

    def handle_notification_error(self, exception, request):
        log.critical(exception)
        return self.ERROR_REPLY

    def handle_data_error(self, exception, text):
        log.warn((exception, text))
        return self.ERROR_REPLY

    def extract_text(self, text):
        """Usually incoming SMS notfications contain Large Account id, a
        separator and some text identifier. This method has to filter out any text in the incoming
        message that is useless in terms of further identification."""

        try:
            prefix, suffix = text.split(".")
            return prefix, suffix
        except ValueError, e:
            log.warn((text, e))

    def get_large_account(self, la_number, text):
        """You may choose to re-implement this method to make more sophisticated
        Large Account finding."""

        prefix, suffix = self.extract_text(text)
        try:
            la = LargeAccount.objects.get(number = la_number, prefixes__value = prefix)
        except LargeAccount.DoesNotExist, e:
            log.info("LA %s for prefix %s is not configured. Invalid SMS.")
            self.handle_data_error(e, text)
        except LargeAccount.MultipleObjectsReturned, e:
            la = LargeAccount.objects.filter(number = la_number, prefixes__value = prefix)[0]
            log.warn("Multiple LA match. Picking first one: %s" % la)
        return la

    def dispatch_purchase(self, la, msisdn, text):
        """After the incoming message has been parsed succesfully and everything
        went with no errors, a signal indicating received notifictions is sent.
        It is your duty to connect to the signal and run purchase handling."""

        extracted_text = self.extract_text(text)
        log.debug("Dispatching purchase: %s %s %s" % (la, msisdn, extracted_text))
        sms_received.send(sender = self.__class__, la = la, msisdn = msisdn, \
                extracted_text = extracted_text)

def get_service_provider(instance = True, **kwargs):
    """Since every service provider (== service broker) has to be registered in
    your application within sms.models.ServiceProviderData record, this utility
    method is a convinient factory producing ServiceProvider instances (or
    classes - depending on the instance bool argument)
    on-the-fly based on keyword arguments -- usually the slug. """

    log.debug("Getting service provider: %s" % kwargs)
    sp = ServiceProviderData.objects.get(**kwargs)
    mod, kls = sp.module.rsplit('.', 1)
    m = __import__(mod, fromlist=[kls])
    Klass = getattr(m, kls)
    if instance:
        return Klass(db_id = sp.id)
    return Klass
