from google.cloud import storage


def upload_file(tenant_id,file_name,local_file_path):
    client = storage.Client()
    # https://console.cloud.google.com/storage/browser/[bucket-id]/
    bucket = client.get_bucket('xview')
    blob2 = bucket.blob('cert/'+tenant_id+'/'+file_name)
    blob2.upload_from_filename(filename=local_file_path)
