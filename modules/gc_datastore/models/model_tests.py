import os

from CallSession import CallSession
from CallObject import CallObject

if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
    print('[ERROR] environment does not have google app credential')
    print('see more: https://cloud.google.com/docs/authentication/production#providing_credentials_to_your_application')
    exit(1)

"""
read more on datastore concept:
https://cloud.google.com/datastore/docs/concepts/entities#datastore-basic-entity-python
"""

cs = CallSession(ns='test-ns').put(caller_name='John Doe',
                                   caller_no='2323')
print('call session:', cs)

co = CallObject(ns='test-ns').put(url='http://example.com',
                                  call_session_key=cs.key)
print('call object:', co)
