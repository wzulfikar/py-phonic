from google.cloud import datastore
from google.cloud.datastore.entity import Entity
from google.cloud.datastore.key import Key
from util import mysql_now


class CallObject:
    def __init__(self, ns: str):
        self.c = datastore.Client()
        self.kind = self.__class__.__name__
        self.ns = ns

    def put(self, url: str, call_session_key: Key) -> Entity:
        obj = {
            'url': url,
            'created_at': mysql_now(),
        }

        key = self.c.key(self.kind,
                         namespace=self.ns,
                         parent=call_session_key)
        ent = datastore.Entity(key=key)
        ent.update(obj)

        self.c.put(ent)
        return ent
