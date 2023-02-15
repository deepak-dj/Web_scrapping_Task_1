import pymongo

class MongodbConnection:
    def __init__(self,client_url) -> None:
        self.client_url = client_url
    
    def mongo_client(self):
        try:
            client = pymongo.MongoClient('{}'.format(self.client_url),connectTimeoutMS=300000)
            db = client.test
            return client
        except Exception as e:
            return e

    def database_collection(self):
        try:
            client = self.mongo_client()
            database = client['ineuron_courses']
            collection = database['courses']
            return collection
        except Exception as e:
            return e
        
    def insert_data(self,data):
        try:
            collec = self.database_collection()
            collec.insert_one(data)
        except Exception as e:
            return e

      