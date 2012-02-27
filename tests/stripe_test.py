# -*- coding: utf-8 -*-

import os, os.path, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest

from tornado_api import Stripe

DUMMY_PLAN = {
    'amount': 2000,
    'interval': 'month',
    'name': 'Amazing Gold Plan',
    'currency': 'usd',
    'id': 'stripe-test-gold'
 }

class UrlGenerationTest(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.stripe = Stripe('api_key', blocking=True)

    def resource_without_id_test(self):
        '''
        self.stripe.charges.url      should == https://api_key:@api.stripe.com/v1/charges
        self.stripe.customers.url    should == https://api_key:@api.stripe.com/v1/customers
        self.stripe.invoices.url     should == https://api_key:@api.stripe.com/v1/invoices
        self.stripe.invoiceitems.url should == https://api_key:@api.stripe.com/v1/invoiceitems
        self.stripe.tokens.url       should == https://api_key:@api.stripe.com/v1/tokens
        self.stripe.events.url       should == https://api_key:@api.stripe.com/v1/events
        self.stripe.plans.url        should == https://api_key:@api.stripe.com/v1/plans
        self.stripe.coupons.url      should == https://api_key:@api.stripe.com/v1/coupons
        '''
        for resource in ['charges', 'customers', 'invoices', 'invoiceitems', 'tokens', 'events', 'plans', 'coupons']:
            expectation = '%s/%s' % (self.stripe.api_endpoint, resource)

            getattr(self.stripe, resource)  # Equivalent of self.stripe.charges
            self.assertEqual(self.stripe.url, expectation)
            self.stripe.reset_url()


    def resource_with_id_test(self):
        '''
        self.stripe.charges.id('charge_id').url        should == https://api_key:@api.stripe.com/v1/charges/charge_id
        self.stripe.customers.id('customer_id').url    should == https://api_key:@api.stripe.com/v1/customers/customer_id
        self.stripe.invoices.id('invoice_id').url      should == https://api_key:@api.stripe.com/v1/invoices/invoice_id
        self.stripe.invoiceitems.id('invoiceitem').url should == https://api_key:@api.stripe.com/v1/invoiceitems/invoiceitem_id
        self.stripe.tokens.id('token_id').url          should == https://api_key:@api.stripe.com/v1/tokens/token_id
        self.stripe.events.id('event_id').url          should == https://api_key:@api.stripe.com/v1/events/event_id
        self.stripe.plans.id('plan_id').url            should == https://api_key:@api.stripe.com/v1/plans/plan_id
        self.stripe.coupons.id('coupon_id').url        should == https://api_key:@api.stripe.com/v1/coupons/coupon_id
        '''
        for resource in ['charges', 'customers', 'invoices', 'invoiceitems', 'tokens', 'events']:
            id = resource[:-1] + '_id'
            expectation = '%s/%s/%s' % (self.stripe.api_endpoint, resource, id)

            getattr(self.stripe, resource)  # Equivalent of self.stripe.charges
            self.stripe.id(id)

            self.assertEqual(self.stripe.url, expectation)
            self.stripe.reset_url()


    def resource_after_id_test(self):
        '''
        self.stripe.customers.id('customer_id').subscription.url
            should == https://api_key:@api.stripe.com/v1/customers/customer_id/subscription
        '''
        id = 'customer_id'
        expectation = '%s/customers/%s/subscription' % (self.stripe.api_endpoint, id)

        self.stripe.customers.id(id).subscription

        self.assertEqual(self.stripe.url, expectation)
        self.stripe.reset_url()


    def nested_resource_test(self):
        '''
        self.stripe.invoices.incoming.url
            should == https://api_key:@api.stripe.com/v1/invoices/incoming
        '''
        expectation = '%s/invoices/incoming' % (self.stripe.api_endpoint)

        self.stripe.invoices.incoming

        self.assertEqual(self.stripe.url, expectation)
        self.stripe.reset_url()


class BadApiKeyTest(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.stripe = Stripe('api_key', blocking=True)


    def bad_api_key_get_test(self):
        try:
            self.stripe.plans.get()
        except Exception, e:
            self.assertEqual(e.__class__.__name__, 'HTTPError')
            self.assertTrue(str(e).find('401') > -1)
            self.assertTrue(str(e).find('Unauthorized') > -1)


class GoodApiKeyTest(unittest.TestCase):
    '''
    To run this test on CLI:
        export STRIPE_API_KEY=your-stripe-api-key; nosetests
    '''
    def setUp(self):
        unittest.TestCase.setUp(self)
        api_key = os.environ.get('STRIPE_API_KEY', None)
        if not api_key:
            raise KeyError("You must set STRIPE_API_KEY environment variable. Example: export STRIPE_API_KEY=your-stripe-api-key; nosetests")

        self.stripe = Stripe(api_key, blocking=True)


class PlansTest(GoodApiKeyTest):
    def crud_test(self):
        # Test creating DUMMY_PLAN
        self.stripe.plans.post(**DUMMY_PLAN)

        # Test getting created DUMMY_PLAN
        plan = self.stripe.plans.id(DUMMY_PLAN['id']).get()
        for key in DUMMY_PLAN.keys():
            self.assertEqual(plan[key], DUMMY_PLAN[key])

        # Test deletion of DUMMY_PLAN
        self.stripe.plans.id(DUMMY_PLAN['id']).delete()

        # After deletion, such plan should not exists.
        try:
            plan = self.stripe.plans.id(DUMMY_PLAN['id']).get()
        except Exception, e:
            self.assertEqual(e.__class__.__name__, 'HTTPError')
            self.assertTrue(str(e).find('404') > -1)
            self.assertTrue(str(e).find('Not Found') > -1)


