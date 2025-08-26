import os
import json
import firebase_admin
from firebase_admin import credentials, storage
from google.cloud import storage as gcs

class FirebaseStorage:
    def __init__(self):
        self.bucket = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get Firebase config from environment variable
                firebase_config = os.environ.get('FIREBASE_CONFIG')
                
                if firebase_config:
                    # Parse JSON config from environment variable
                    config_dict = json.loads(firebase_config)
                    cred = credentials.Certificate(config_dict)
                else:
                    # Fallback to service account file
                    service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'firebase-service-account.json')
                    if os.path.exists(service_account_path):
                        cred = credentials.Certificate(service_account_path)
                    else:
                        print("Warning: Firebase credentials not found. File upload will not work.")
                        return
                
                # Initialize Firebase app
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'your-project-id.appspot.com')
                })
            
            # Get storage bucket
            self.bucket = storage.bucket()
            print("Firebase Storage initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            self.bucket = None
    
    def upload_file(self, file_obj, filename, folder='uploads'):
        """Upload file to Firebase Storage"""
        if not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            # Create blob path
            blob_path = f"{folder}/{filename}"
            blob = self.bucket.blob(blob_path)
            
            # Upload file
            blob.upload_from_file(file_obj, content_type=file_obj.content_type)
            
            # Make blob publicly readable (optional)
            blob.make_public()
            
            # Return public URL
            return blob.public_url
            
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e
    
    def delete_file(self, file_path):
        """Delete file from Firebase Storage"""
        if not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, file_path):
        """Get public URL for a file"""
        if not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            blob = self.bucket.blob(file_path)
            return blob.public_url
        except Exception as e:
            print(f"Error getting file URL: {e}")
            return None

# Global instance
firebase_storage = FirebaseStorage()
