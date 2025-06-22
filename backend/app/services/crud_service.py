from motor.core import AgnosticCollection
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, List, Optional, Union
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CRUDService:
    """Generic CRUD service for MongoDB operations"""

    def __init__(self, collection: AgnosticCollection):
        self.collection = collection

    def _convert_objectid_to_string(self, obj: Any) -> Any:
        """Recursively convert ObjectId to string for JSON serialization"""
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, dict):
            return {
                key: self._convert_objectid_to_string(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._convert_objectid_to_string(item) for item in obj]
        else:
            return obj

    # CREATE operations
    async def create_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single document"""
        try:
            # Add timestamps
            document["created_at"] = datetime.utcnow()
            document["updated_at"] = datetime.utcnow()

            result = await self.collection.insert_one(document)
            document["_id"] = result.inserted_id

            logger.info(f"Created document with ID: {result.inserted_id}")
            return self._convert_objectid_to_string(document)
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise e

    async def create_many(
        self, documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create multiple documents"""
        try:
            # Add timestamps to all documents
            for doc in documents:
                doc["created_at"] = datetime.utcnow()
                doc["updated_at"] = datetime.utcnow()

            result = await self.collection.insert_many(documents)

            # Add _id to documents
            for i, doc in enumerate(documents):
                doc["_id"] = result.inserted_ids[i]

            logger.info(f"Created {len(documents)} documents")
            return [self._convert_objectid_to_string(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error creating documents: {e}")
            raise e

    # READ operations
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        try:
            document = await self.collection.find_one(filter_dict)
            return self._convert_objectid_to_string(document) if document else None
        except Exception as e:
            logger.error(f"Error finding document: {e}")
            raise e

    async def find_by_id(
        self, document_id: Union[str, ObjectId]
    ) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        try:
            if isinstance(document_id, str):
                document_id = ObjectId(document_id)

            document = await self.collection.find_one({"_id": document_id})
            return self._convert_objectid_to_string(document) if document else None
        except Exception as e:
            logger.error(f"Error finding document by ID: {e}")
            raise e

    async def find_many(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """Find multiple documents with pagination and sorting"""
        try:
            filter_dict = filter_dict or {}

            cursor = self.collection.find(filter_dict)

            # Apply sorting
            if sort_by:
                cursor = cursor.sort(sort_by)

            # Apply pagination
            cursor = cursor.skip(skip).limit(limit)

            documents = await cursor.to_list(length=limit)
            return [self._convert_objectid_to_string(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            raise e

    async def count_documents(
        self, filter_dict: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count documents matching filter"""
        try:
            filter_dict = filter_dict or {}
            count = await self.collection.count_documents(filter_dict)
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise e

    # UPDATE operations
    async def update_one(
        self,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        upsert: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Update a single document"""
        try:
            # Add updated timestamp
            update_dict["updated_at"] = datetime.utcnow()

            # Use $set to update only specified fields
            update_operation = {"$set": update_dict}

            result = await self.collection.update_one(
                filter_dict, update_operation, upsert=upsert
            )

            if result.modified_count > 0:
                logger.info(f"Updated document: {filter_dict}")
                return await self.find_one(filter_dict)
            elif result.upserted_id:
                logger.info(f"Upserted document with ID: {result.upserted_id}")
                return await self.find_by_id(result.upserted_id)
            else:
                logger.warning(f"No document found to update: {filter_dict}")
                return None
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise e

    async def update_by_id(
        self, document_id: Union[str, ObjectId], update_dict: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update document by ID"""
        try:
            if isinstance(document_id, str):
                document_id = ObjectId(document_id)

            return await self.update_one({"_id": document_id}, update_dict)
        except Exception as e:
            logger.error(f"Error updating document by ID: {e}")
            raise e

    async def update_many(
        self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]
    ) -> int:
        """Update multiple documents"""
        try:
            # Add updated timestamp
            update_dict["updated_at"] = datetime.utcnow()

            update_operation = {"$set": update_dict}
            result = await self.collection.update_many(filter_dict, update_operation)

            logger.info(f"Updated {result.modified_count} documents")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise e

    # DELETE operations
    async def delete_one(self, filter_dict: Dict[str, Any]) -> bool:
        """Delete a single document"""
        try:
            result = await self.collection.delete_one(filter_dict)

            if result.deleted_count > 0:
                logger.info(f"Deleted document: {filter_dict}")
                return True
            else:
                logger.warning(f"No document found to delete: {filter_dict}")
                return False
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise e

    async def delete_by_id(self, document_id: Union[str, ObjectId]) -> bool:
        """Delete document by ID"""
        try:
            if isinstance(document_id, str):
                document_id = ObjectId(document_id)

            return await self.delete_one({"_id": document_id})
        except Exception as e:
            logger.error(f"Error deleting document by ID: {e}")
            raise e

    async def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """Delete multiple documents"""
        try:
            result = await self.collection.delete_many(filter_dict)

            logger.info(f"Deleted {result.deleted_count} documents")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise e

    # Utility methods
    async def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """Check if document exists"""
        try:
            count = await self.collection.count_documents(filter_dict, limit=1)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            raise e

    async def find_one_and_update(
        self,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        return_document: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Find and update a document atomically"""
        try:
            update_dict["updated_at"] = datetime.utcnow()
            update_operation = {"$set": update_dict}

            result = await self.collection.find_one_and_update(
                filter_dict,
                update_operation,
                return_document=True if return_document else False,
            )

            return self._convert_objectid_to_string(result) if result else None
        except Exception as e:
            logger.error(f"Error in find_one_and_update: {e}")
            raise e

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation pipeline"""
        try:
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            return [self._convert_objectid_to_string(doc) for doc in results]
        except Exception as e:
            logger.error(f"Error in aggregation: {e}")
            raise e


# Factory function to create CRUD service for a collection
def create_crud_service(collection_name: str):
    """Factory function to create a CRUD service for a specific collection"""
    from ..database import get_collection

    collection = get_collection(collection_name)
    return CRUDService(collection)
