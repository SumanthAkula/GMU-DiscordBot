import gridfs
import pymongo
from bson import ObjectId


class DatabaseController:
    def __init__(self, connection_url: str, database_name: str):
        self.connection_url = connection_url
        self.connection = pymongo.MongoClient(connection_url)
        self.db = self.connection[database_name]

    def __check_collection(self, collection_name: str):
        if collection_name not in self.db.list_collection_names():
            raise InvalidCollectionError(f"Collection '{collection_name}' does not exist!")

    def write(self, collection_name: str, data: dict) -> ObjectId:
        # TODO: check if database is full
        return self.db[collection_name].insert_one(data)

    def write_gridfs(self, filename: str, path: str):
        fs = gridfs.GridFS(self.connection.grid_file)
        with open(path + filename, "rb") as file:
            fs.put(file.read(), filename=filename)

    def delete_gridfs(self, filename: str):
        result = self.connection.grid_file.fs.files.find(
            {
                "filename": filename
            }
        )
        result = list(result)
        print(result[0]["_id"])

    def query(self, collection_name: str, query: dict) -> dict:
        result = self.db[collection_name].find(query)
        return dict(result)


# ERRORS
class InvalidDatabaseError(Exception):
    """
    Raised when DatabaseController is initialized with a database that does not exist
    """
    pass


class InvalidCollectionError(Exception):
    """
    Raised when trying to write to a collection that does not exist
    """
    pass


class DatabaseFullError(Exception):
    """
    Raised when writing to a database that has no space left in it
    """
    pass
