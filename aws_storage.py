import os
import uuid
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class AWSS3Storage:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = None
        self.initialize_s3()
    
    def initialize_s3(self):
        """Initialize AWS S3 client"""
        try:
            # Get AWS credentials from environment variables
            aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
            self.bucket_name = os.environ.get('AWS_S3_BUCKET_NAME')
            
            if not all([aws_access_key, aws_secret_key, self.bucket_name]):
                print("Warning: AWS credentials or bucket name not found. File upload will not work.")
                return
            
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            
            # Test connection by checking if bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                print("AWS S3 initialized successfully")
            except ClientError as e:
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    print(f"Warning: S3 bucket '{self.bucket_name}' not found")
                else:
                    print(f"Warning: Cannot access S3 bucket: {e}")
                self.s3_client = None
            
        except NoCredentialsError:
            print("Warning: AWS credentials not found. File upload will not work.")
            self.s3_client = None
        except Exception as e:
            print(f"Error initializing AWS S3: {e}")
            self.s3_client = None
    
    def upload_file(self, file_obj, filename, folder='uploads'):
        """Upload file to AWS S3"""
        if not self.s3_client or not self.bucket_name:
            raise Exception("AWS S3 not initialized")
        
        try:
            # Create S3 key (path)
            s3_key = f"{folder}/{filename}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file_obj.content_type,
                    'ACL': 'public-read'  # Make file publicly readable
                }
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            return file_url
            
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            raise e
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e
    
    def delete_file(self, file_url):
        """Delete file from AWS S3"""
        if not self.s3_client or not self.bucket_name:
            raise Exception("AWS S3 not initialized")
        
        try:
            # Extract S3 key from URL
            # URL format: https://bucket-name.s3.amazonaws.com/folder/filename
            if f"{self.bucket_name}.s3.amazonaws.com" in file_url:
                s3_key = file_url.split(f"{self.bucket_name}.s3.amazonaws.com/")[1]
                
                # Delete file
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                return True
            else:
                print(f"Invalid S3 URL format: {file_url}")
                return False
                
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, s3_key):
        """Get public URL for a file"""
        if not self.bucket_name:
            return None
        
        return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
    
    def generate_presigned_url(self, s3_key, expiration=3600):
        """Generate a presigned URL for secure file access"""
        if not self.s3_client or not self.bucket_name:
            return None
        
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

# Global instance
aws_storage = AWSS3Storage()
