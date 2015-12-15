#!/usr/bin/env python

import sys
sys.path.append(".")

from api import GET, POST, PUT, DELETE, Results
import sys
import pprint

verbose = False

get = GET()
post = POST()
put = PUT()
delete = DELETE()

# Requirement: the populate_database.py script must be run on the jetlaunch database prior to running these tests

contacts = {
'registrant': {'address_1': '5808 Lake Washington BLVD STE 300',
           'address_2': None,
           'city': 'Kirkland',
           'country': 'US',
           'email_address': 'sales@enom.com',
           'fax': None,
           'first_name': 'New Registrant',
           'full_country': None,
           'job_title': '-',
           'last_name': 'Nelson',
           'organization': None,
           'phone': '+1.4252984500',
           'phone_ext': None,
           'postal_code': '98033',
           'state_province': 'WA',
           'state_province_choice': 'S'}}

domain = 'superunique124040.com'
print domain

# all domains for a customer
response = get('/domains', params={"customer_id": 1})
print response

# available?
response = get('/domains/{domain}/available'.format(domain=domain), params={})
print response

# create domain
if response and response['available']:
    response = post('/domains/{domain}'.format(domain=domain), params={"customer_id": 1, 'contacts': contacts})
    print response
raw_input("Hit Enter to Continue")

# get success
response = get('/domains/{domain}'.format(domain=domain), params={"customer_id": 1})
print response

# put success
if response:
    response['name_server'] = 'ns.rightside.co'
    response['contacts'] = contacts
    pprint.pprint(response)
    response = put('/domains/{domain}'.format(domain=domain), params=response)
    print response

# get success
response = get('/domains/{domain}'.format(domain=domain), params={"customer_id": 1})
print response

fail_domain = 'nonexistingdomain.com'
# get fail
response = get('/domains/{domain}'.format(domain=fail_domain), params={})
print response

# put fail
response = put('/domains/{domain}'.format(domain=fail_domain), params=response)
print response


# def list_validation(reply):
#     assert reply['pagination'], 'Pagination expected'
#     assert type(reply['response_data']) is list, 'List expected for response_data'
