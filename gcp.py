from google.cloud import storage
import os

def upload_to_bucket(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # Initialize a storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob object from the filepath
    blob = bucket.blob(destination_blob_name)
    
    # Upload the file to a destination
    blob.upload_from_filename(source_file_name)
    
    # Note: Removed blob.make_public() as it's not needed with uniform bucket-level access
    
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    print(f"Public URL: https://storage.googleapis.com/{bucket_name}/{destination_blob_name}")

# Set these variables to your values
bucket_name = 'iot_pro'
source_file_name = './last_detection.jpg'
destination_blob_name = 'uploaded-image.jpg'

upload_to_bucket(bucket_name, source_file_name, destination_blob_name)
