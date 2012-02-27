## What is tornado_api

tornado_api is a collection of Mixins and asynchronous HTTP libraries for [Tornado Web Framework](http://www.tornadoweb.org/).


## FacebookGraphMixin

Re-implementation of Tornado's OAuth2 Mixin.


## FoursquareMixin

OAuth2 Mixin for Foursquare. Once authorized via authorize_redirect(), you can call Foursquare API using foursquare_request()


## tornado_api.Stripe

A complete implementation of Stripe v1 API using Tornado AsyncHTTPClient.

### Initialization

```python
    #
	# By default, blocking is set to False.
	# If blocking is set to True, then it uses Tornado blocking HTTP client.
	#
	stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY, blocking=True)
```

### Building URL

tornado_api.Stripe maps to Stripe Curl URL exactly one-to-one.

/v1/charges

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.charges
```

/v1/charges/{CHARGE_ID}

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.charges.id(CHARGE_ID)
```

/v1/customers

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.customers
```

/v1/customers/{CUSTOMER_ID}

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.customers.id(CUSTOMER_ID)
```

/v1/customers/{CUSTOMER_ID}/subscription

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.customers.id(CUSTOMER_ID).subscription
```

/v1/invoices

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.invoices
```

/v1/invoices/{INVOICE_ID}

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.invoices.id(INVOICE_ID)
```

/v1/invoiceitems

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.invoiceitems
```

/v1/invoiceitems/{INVOICEITEM_ID}

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.invoiceitems.id(INVOICEITEM_ID)
```

/v1/tokens

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.tokens
```

/v1/tokens/{TOKEN_ID}

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.tokens.id(TOKEN_ID)
```

/v1/events

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.events
```

/v1/events/{EVENT_ID}

```python
    stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
    stripe.events.id(EVENT_ID)
```

### Performing HTTP request

GET

```python
  	stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
  	stripe.plans.get()
  	stripe.plans.id(PLAN_ID).get()
```

POST

```python
	DUMMY_PLAN = {
    	'amount': 2000,
    	'interval': 'month',
    	'name': 'Amazing Gold Plan',
    	'currency': 'usd',
    	'id': 'stripe-test-gold'
 	}
  	stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
	stripe.plans.post(**DUMMY_PLAN)
```

DELETE

```python
	stripe = tornado_api.Stripe(YOUR_STRIPE_API_KEY)
  	stripe.plans.id(DUMMY_PLAN['id']).delete()
```

## tornado_api.Twitter

Requirement:

```
pip install twitter
```

Based on [Twitter module](http://mike.verdone.ca/twitter/). The only 2 differences:

  * The HTTP client have been replaced by Tornado AsyncHTTPClient.

  * \_\_call\_\_() accepts _callback as keyword argument.
