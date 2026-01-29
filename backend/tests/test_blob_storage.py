import unittest
from unittest.mock import MagicMock, patch
from fastapi import UploadFile
import io
import os

class TestS3BlobStorage(unittest.TestCase):
    @patch("backend.services.blob_storage.config")
    @patch("backend.services.blob_storage.boto3")
    def test_save_upload(self, mock_boto3, mock_config):
        from backend.services.blob_storage import S3BlobStorage
        
        mock_config.S3_BUCKET_NAME = "test-bucket"
        mock_config.AWS_ACCESS_KEY_ID = "test-key"
        mock_config.AWS_SECRET_ACCESS_KEY = "test-secret"
        
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        storage = S3BlobStorage()
        
        file = UploadFile(filename="test.pdf", file=io.BytesIO(b"content"))
        key = storage.save_upload(file, "session123")
        
        assert key == "session123/test.pdf"
        mock_s3.upload_fileobj.assert_called_once()

    @patch("backend.services.blob_storage.config")
    @patch("backend.services.blob_storage.boto3")
    def test_get_file_path(self, mock_boto3, mock_config):
        from backend.services.blob_storage import S3BlobStorage
        
        mock_config.S3_BUCKET_NAME = "test-bucket"
        mock_config.AWS_ACCESS_KEY_ID = "test-key"
        mock_config.AWS_SECRET_ACCESS_KEY = "test-secret"
        
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        storage = S3BlobStorage()
        
        path = storage.get_file_path("session123/test.pdf")
        
        assert os.path.exists(path)
        assert path.endswith(".pdf")
        
        mock_s3.download_fileobj.assert_called_once()
        
        os.unlink(path)
