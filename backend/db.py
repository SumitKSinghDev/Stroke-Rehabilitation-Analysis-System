import json
import uuid
from datetime import datetime
from threading import Lock
import pymongo
from bson import ObjectId
from backend.config import MONGODB_URL, DATABASE_NAME, DATABASE_DIR, USE_MOCK_DB

# Thread lock for file-based DB access
file_lock = Lock()

class MockCollection:
    """Mock MongoDB collection using local JSON files."""
    def __init__(self, name: str):
        self.name = name
        self.file_path = DATABASE_DIR / f"{name}.json"
        if not self.file_path.exists():
            self._write_data([])

    def _read_data(self):
        with file_lock:
            try:
                with open(self.file_path, "r") as f:
                    content = f.read().strip()
                    return json.loads(content) if content else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []

    def _write_data(self, data):
        with file_lock:
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4, default=str)

    def find_one(self, query: dict):
        data = self._read_data()
        for item in data:
            if self._match(item, query):
                return item
        return None

    def find(self, query: dict = None):
        if query is None:
            query = {}
        data = self._read_data()
        results = []
        for item in data:
            if self._match(item, query):
                results.append(item)
        return results

    def insert_one(self, document: dict):
        data = self._read_data()
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        elif isinstance(doc["_id"], ObjectId):
            doc["_id"] = str(doc["_id"])
        
        # Serialize datetimes to ISO strings
        for k, v in doc.items():
            if isinstance(v, datetime):
                doc[k] = v.isoformat()
            elif isinstance(v, dict):
                doc[k] = self._serialize_dict(v)
            elif isinstance(v, list):
                doc[k] = [self._serialize_dict(x) if isinstance(x, dict) else (x.isoformat() if isinstance(x, datetime) else x) for x in v]

        data.append(doc)
        self._write_data(data)
        return InsertOneResult(doc["_id"])

    def update_one(self, query: dict, update: dict):
        data = self._read_data()
        modified = 0
        
        # We only support simple $set updates for our mock
        set_data = update.get("$set", {})
        
        # Serialize datetimes
        set_data = self._serialize_dict(set_data)

        for item in data:
            if self._match(item, query):
                for k, v in set_data.items():
                    # Handle dotted paths if any, or simple fields
                    if "." in k:
                        parts = k.split(".")
                        curr = item
                        for part in parts[:-1]:
                            if part not in curr:
                                curr[part] = {}
                            curr = curr[part]
                        curr[parts[-1]] = v
                    else:
                        item[k] = v
                modified = 1
                break
        
        if modified:
            self._write_data(data)
        return UpdateResult(modified)

    def delete_one(self, query: dict):
        data = self._read_data()
        initial_len = len(data)
        data = [item for item in data if not self._match(item, query)]
        modified = initial_len - len(data)
        if modified > 0:
            self._write_data(data)
        return DeleteResult(modified)

    def count_documents(self, query: dict = None):
        if query is None:
            query = {}
        data = self._read_data()
        count = 0
        for item in data:
            if self._match(item, query):
                count += 1
        return count

    def _match(self, item: dict, query: dict) -> bool:
        for q_key, q_val in query.items():
            if q_key == "_id" and isinstance(q_val, dict) and "$in" in q_val:
                item_val = item.get("_id")
                if item_val not in [str(x) for x in q_val["$in"]]:
                    return False
                continue

            # Simple field match
            item_val = item.get(q_key)
            
            # Sub-document match support (dotted query)
            if "." in q_key:
                parts = q_key.split(".")
                curr = item
                for part in parts:
                    if isinstance(curr, dict) and part in curr:
                        curr = curr[part]
                    else:
                        curr = None
                        break
                item_val = curr

            # Match criteria
            if isinstance(q_val, dict):
                # E.g., {"$in": [...]} or {"$gt": ...}
                if "$in" in q_val:
                    if item_val not in q_val["$in"]:
                        return False
                elif "$gt" in q_val:
                    if not (item_val and item_val > q_val["$gt"]):
                        return False
                elif "$lt" in q_val:
                    if not (item_val and item_val < q_val["$lt"]):
                        return False
            else:
                # Direct equality
                if str(item_val) != str(q_val):
                    return False
        return True

    def _serialize_dict(self, d: dict) -> dict:
        new_dict = {}
        for k, v in d.items():
            if isinstance(v, datetime):
                new_dict[k] = v.isoformat()
            elif isinstance(v, dict):
                new_dict[k] = self._serialize_dict(v)
            elif isinstance(v, list):
                new_dict[k] = [self._serialize_dict(x) if isinstance(x, dict) else (x.isoformat() if isinstance(x, datetime) else x) for x in v]
            else:
                new_dict[k] = v
        return new_dict

class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class UpdateResult:
    def __init__(self, modified_count):
        self.modified_count = modified_count
        self.matched_count = modified_count

class DeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


# Database Client Manager
class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.use_mock = USE_MOCK_DB

        if not self.use_mock:
            try:
                # Short timeout to fail quickly if Mongo is down
                self.client = pymongo.MongoClient(MONGODB_URL, serverSelectionTimeoutMS=2000)
                # Verify connection
                self.client.server_info()
                self.db = self.client[DATABASE_NAME]
                print("Successfully connected to MongoDB.")
            except Exception as e:
                print(f"MongoDB connection failed: {e}. Falling back to file-based JSON DB.")
                self.use_mock = True

    def get_collection(self, name: str):
        if self.use_mock:
            return MockCollection(name)
        return self.db[name]

# Global database manager instance
db_manager = DatabaseManager()

def get_collection(name: str):
    return db_manager.get_collection(name)
