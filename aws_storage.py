import os
import uuid
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError

class CloudinaryStorage:
    def __init__(self):
        self.initialized = False
        self.initialize_cloudinary()
    
    def initialize_cloudinary(self):
        """Initialize Cloudinary client"""
        try:
            # Get Cloudinary credentials from environment variables
            cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
            api_key = os.environ.get('CLOUDINARY_API_KEY')
            api_secret = os.environ.get('CLOUDINARY_API_SECRET')
            
            if not all([cloud_name, api_key, api_secret]):
                print("Warning: Cloudinary credentials not found. File upload will not work.")
                return
            
            # Configure Cloudinary
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )
            
            # Test connection
            try:
                cloudinary.api.ping()
                self.initialized = True
                print("Cloudinary initialized successfully")
            except CloudinaryError as e:
                print(f"Warning: Cannot connect to Cloudinary: {e}")
                self.initialized = False
            
        except Exception as e:
            print(f"Error initializing Cloudinary: {e}")
            self.initialized = False
    
    def upload_file(self, file_obj, filename, folder='appointments'):
        """Upload file to Cloudinary"""
        if not self.initialized:
            raise Exception("Cloudinary not initialized")
        
        try:
            # Generate unique public ID
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            public_id = f"{folder}/{uuid.uuid4()}_{filename.replace('.' + file_extension, '')}"
            
            # Upload file
            result = cloudinary.uploader.upload(
                file_obj,
                public_id=public_id,
                resource_type="auto",  # Auto-detect file type
                folder=folder,
                use_filename=True,
                unique_filename=True,
                overwrite=False
            )
            
            # Return the secure URL
            return result['secure_url']
            
        except CloudinaryError as e:
            print(f"Error uploading file to Cloudinary: {e}")
            raise e
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e
    
    def delete_file(self, file_url):
        """Delete file from Cloudinary"""
        if not self.initialized:
            raise Exception("Cloudinary not initialized")
        
        try:
            # Extract public ID from URL
            # Cloudinary URL format: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/filename.ext
            if 'res.cloudinary.com' in file_url:
                # Split URL and extract public ID
                url_parts = file_url.split('/')
                if len(url_parts) >= 7:
                    # Get everything after /upload/v123456/
                    version_index = -1
                    for i, part in enumerate(url_parts):
                        if part.startswith('v') and part[1:].isdigit():
                            version_index = i
                            break
                    
                    if version_index != -1 and version_index + 1 < len(url_parts):
                        public_id_parts = url_parts[version_index + 1:]
                        public_id = '/'.join(public_id_parts)
                        # Remove file extension
                        public_id = public_id.rsplit('.', 1)[0]
                        
                        # Delete file
                        result = cloudinary.uploader.destroy(public_id)
                        return result.get('result') == 'ok'
            
            print(f"Could not extract public ID from URL: {file_url}")
            return False
                
        except CloudinaryError as e:
            print(f"Error deleting file from Cloudinary: {e}")
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_optimized_url(self, file_url, width=None, height=None, quality="auto"):
        """Get optimized URL for images"""
        if not self.initialized or 'res.cloudinary.com' not in file_url:
            return file_url
        
        try:
            # Extract public ID from URL
            url_parts = file_url.split('/')
            version_index = -1
            for i, part in enumerate(url_parts):
                if part.startswith('v') and part[1:].isdigit():
                    version_index = i
                    break
            
            if version_index != -1 and version_index + 1 < len(url_parts):
                public_id_parts = url_parts[version_index + 1:]
                public_id = '/'.join(public_id_parts)
                public_id = public_id.rsplit('.', 1)[0]  # Remove extension
                
                # Build transformation parameters
                transformations = []
                if width:
                    transformations.append(f"w_{width}")
                if height:
                    transformations.append(f"h_{height}")
                if quality:
                    transformations.append(f"q_{quality}")
                
                # Generate optimized URL
                if transformations:
                    transformation_string = ','.join(transformations)
                    return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation_string)
            
            return file_url
            
        except Exception as e:
            print(f"Error generating optimized URL: {e}")
            return file_url

# Global instance
cloudinary_storage = CloudinaryStorage()
