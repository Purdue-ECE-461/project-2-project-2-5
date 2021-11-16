
from flask import Flask, render_template
# from werkzeug.datastructures import FileStorage
from google.cloud import storage
# from PIL import Image
# from google.oauth2 import service_account


app = Flask(__name__)

@app.route("/")
def homepage():
    return "<p>Hello, World!</p>"

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    # gcp_json_credentials_dict = json.loads(gcp_credentials_string)
    # credentials = service_account.Credentials.from_service_account_info(gcp_json_credentials_dict)
    # storage_client = storage.Client(project=gcp_json_credentials_dict['project-2-331602'], credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    # image = Image.open(source_file_name)
    # fs = FileStorage()
    # image.save(fs, format="JPEG")
    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name,destination_blob_name))

def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    # gcp_json_credentials_dict = json.loads(gcp_credentials_string)
    # credentials = service_account.Credentials.from_service_account_info(gcp_json_credentials_dict)
    # storage_client = storage.Client(project=gcp_json_credentials_dict['project-2-331602'], credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    # image = Image.open(source_file_name)
    # fs = FileStorage()
    # image.save(fs, format="JPEG")
    blob.download_to_filename(destination_file_name)

    print("Downloaded storage object {} from bucket {} to local file {}.".format(source_blob_name, bucket_name, destination_file_name))

if __name__ == "__main__":
    # app.run(debug=True)
    upload_blob("main-registry-461-project-2","smile.zip", "test_zip")
    download_blob("main-registry-461-project-2","test_zip", "download_test.zip")
