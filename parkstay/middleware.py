import re

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from parkstay.models import Booking

CHECKOUT_PATH = re.compile('^/ledger/checkout/checkout')

class BookingTimerMiddleware(object):
    def process_request(self, request):
        if 'ps_booking' in request.session:
            try:
                booking = Booking.objects.get(pk=request.session['ps_booking'])
            except:
                # no idea what object is in self.request.session['ps_booking'], ditch it
                del request.session['ps_booking']
                return
            if booking.booking_type != 3:
                # booking in the session is not a temporary type, ditch it
                del request.session['ps_booking']
            elif timezone.now() > booking.expiry_time:
                # expiry time has been hit, destroy the Booking then ditch it
                booking.delete()
                del request.session['ps_booking']

        # force a redirect if in the checkout
        if ('ps_booking_internal' not in request.COOKIES) and CHECKOUT_PATH.match(request.path):
            if ('ps_booking' not in request.session) and CHECKOUT_PATH.match(request.path):
                return HttpResponseRedirect(reverse('public_make_booking'))
            else:
                return
            return HttpResponseRedirect(reverse('public_make_booking'))

        return