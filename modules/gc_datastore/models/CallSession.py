from google.cloud import datastore
from google.cloud.datastore.entity import Entity
from util import mysql_now


class CallSession:
    def __init__(self, ns: str):
        self.c = datastore.Client()
        self.kind = self.__class__.__name__
        self.ns = ns

    def put(self, caller_name: str, caller_no: str) -> Entity:
        obj = {
            'caller_name': caller_name,
            'caller_no': caller_no,
            'created_at': mysql_now(),
        }

        key = self.c.key(self.kind,
                         namespace=self.ns)
        ent = datastore.Entity(key=key)
        ent.update(obj)

        self.c.put(ent)
        return ent
