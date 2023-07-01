from django.conf import settings
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection


URI = settings.MONGODB_URI

class Settings:
    def __init__(self, collection):
        self.client = MongoClient(URI)
        self.db = self.client.symptom
        self.c: Collection = self.db[collection]

    def insert(self, pk, fields: dict):
        return self.c.insert_one({
            '_id': pk,
            'settings': fields
        })

    def update(self, pk, fields_values: dict):
        return self.c.update_one(
            {'_id': pk},
            {'$set': {f'settings.{value[0]}': value[1] for value in fields_values.items()}}
        )

    def get(self, pk) -> dict:
        return next(self.c.find({'_id': pk}))['settings']

    def delete(self, pk):
        return self.c.delete_one({'_id': pk})
