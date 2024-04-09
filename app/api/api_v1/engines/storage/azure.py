from azure.storage.blob import BlobClient
from app.config import settings

class AzureEngine:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def upload_blob(self, file_path, container_name, blob_name):
        try:
            blob = BlobClient.from_connection_string(conn_str=self.connection_string, 
                                                    container_name=container_name,
                                                    blob_name=blob_name)
            with open(file_path, "rb") as data:
                blob.upload_blob(data)
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        
    def delete_blob(self, container_name, blob_name):
        try:
            blob = BlobClient.from_connection_string(conn_str=self.connection_string, 
                                                    container_name=container_name,
                                                    blob_name=blob_name)
            blob.delete_blob()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        
azure_storage = AzureEngine(connection_string=settings.azure_connection_string)