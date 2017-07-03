from collections import defaultdict

from django.contrib import messages
from django.template.loader import render_to_string
from oscar.core.loading import get_class

Applicator = get_class('offer.applicator', 'Applicator')


class BasketMessageGenerator(object):

    new_total_template_name = 'basket/messages/new_total.html'
    offer_lost_template_name = 'basket/messages/offer_lost.html'
    offer_gained_template_name = 'basket/messages/offer_gained.html'

    def get_new_total_messages(self, basket, include_buttons=True):
        new_total_messages = []
        # We use the 'include_buttons' parameter to determine whether to show the
        # 'Checkout now' buttons.  We don't want to show these on the basket page.
        msg = render_to_string(self.new_total_template_name,
                               {'basket': basket,
                                'include_buttons': include_buttons})
        new_total_messages.append((messages.INFO, msg))

        return new_total_messages

    def get_offer_lost_messages(self, offers_before, offers_after):
        offer_messages = []
        for offer_id in set(offers_before).difference(offers_after):
            offer = offers_before[offer_id]
            msg = render_to_string(self.offer_lost_template_name, {'offer': offer})
            offer_messages.append((messages.WARNING, msg))
        return offer_messages

    def get_offer_gained_messages(self, offers_before, offers_after):
        offer_messages = []
        for offer_id in set(offers_after).difference(offers_before):
            offer = offers_after[offer_id]
            msg = render_to_string(self.offer_gained_template_name, {'offer': offer})
            offer_messages.append((messages.SUCCESS, msg))
        return offer_messages

    def get_offer_messages(self, offers_before, offers_after):
        offer_messages = []
        offer_messages.extend(self.get_offer_lost_messages(offers_before, offers_after))
        offer_messages.extend(self.get_offer_gained_messages(offers_before, offers_after))
        return offer_messages

    def get_messages(self, basket, offers_before, offers_after, include_buttons=True):
        messages = []
        messages.extend(self.get_offer_messages(offers_before, offers_after))
        messages.extend(self.get_new_total_messages(basket, include_buttons))
        return messages

    def apply_messages(self, request, offers_before):
        """
        Set flash messages triggered by changes to the basket
        """
        # Re-apply offers to see if any new ones are now available
        request.basket.reset_offer_applications()
        Applicator().apply(request.basket, request.user, request)
        offers_after = request.basket.applied_offers()

        for level, msg in self.get_messages(request.basket, offers_before, offers_after):
            messages.add_message(request, level, msg, extra_tags='safe noicon')


class LineOfferConsumer(object):

    def __init__(self, line):
        self.__line = line
        self.__offers = dict()
        self.__affected_quantity = 0
        self.__consumptions = defaultdict(int)

    # private
    def __cache(self, offer):
        self.__offers[offer.pk] = offer

    def __update_affected_quantity(self, quantity):
        if quantity > self.__line.quantity - self.__affected_quantity:
            inc = self.__line.quantity - self.__affected_quantity
        else:
            inc = quantity
        self.__affected_quantity += int(inc)

    # public
    def consume(self, quantity, offer=None):
        self.__update_affected_quantity(quantity)
        if offer:
            available = self.available(offer)
            self.__consumptions[offer.pk] += min(available, quantity)

    def consumed(self, offer=None):
        if not offer:
            return self.__affected_quantity
        self.__cache(offer)
        return self.__consumptions[offer.pk]

    def available(self, offer):
        self.__cache(offer)
        exclusive = any([x.exclusive for x in self.__offers.values()])
        if exclusive:
            consumed = self.__affected_quantity
        else:
            consumed = self.consumed(offer)
        return self.__line.quantity - consumed
