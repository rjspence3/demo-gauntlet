import os
import shutil
from abc import ABC, abstractmethod
from typing import BinaryIO
from fastapi import UploadFile
import boto3
from backend.config import config

class BlobStorage(ABC):
    """
    Abstract base class for blob storage operations.
    """
    @abstractmethod
    def save_upload(self, file: UploadFile, session_id: str) -> str:
        """
        Saves an uploaded file and returns a reference (path or key).
        """
        pass

    @abstractmethod
    def get_file_path(self, file_ref: str) -> str:
        """
        Returns a local file path for the given reference.
        If the file is remote, it should be downloaded to a temp location.
        """
        pass

class LocalBlobStorage(BlobStorage):
    """
    Local filesystem implementation of BlobStorage.
    """
    def __init__(self, base_dir: str = "data/decks"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_upload(self, file: UploadFile, session_id: str) -> str:
        session_dir = os.path.join(self.base_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Sanitize filename (simple version)
        filename = os.path.basename(file.filename) if file.filename else "unknown"
        file_path = os.path.join(session_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return file_path

    def get_file_path(self, file_ref: str) -> str:
        # For local storage, the reference is the path
        if not os.path.exists(file_ref):
            raise FileNotFoundError(f"File not found: {file_ref}")
        return file_ref

class S3BlobStorage(BlobStorage):
    """
    S3 implementation of BlobStorage.
    """
    def __init__(self):
        self.bucket_name = config.S3_BUCKET_NAME
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME is not set")
            
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )

    def save_upload(self, file: UploadFile, session_id: str) -> str:
        # Sanitize filename
        filename = os.path.basename(file.filename) if file.filename else "unknown"
        key = f"{session_id}/{filename}"
        
        # Upload
        self.s3_client.upload_fileobj(file.file, self.bucket_name, key)
        return key

    def get_file_path(self, file_ref: str) -> str:
        # Download to temp file
        import tempfile
        
        # Create a temp file with the correct extension
        ext = os.path.splitext(file_ref)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        
        try:
            self.s3_client.download_fileobj(self.bucket_name, file_ref, tmp)
            tmp.close()
            return tmp.name
        except Exception as e:
            tmp.close()
            os.unlink(tmp.name)
            raise e

def get_blob_storage() -> BlobStorage:
    """
    Factory function to get the configured BlobStorage implementation.
    """
    from backend.config import config
    
    if config.BLOB_STORAGE_TYPE == "s3":
        return S3BlobStorage()
    
    return LocalBlobStorage()
