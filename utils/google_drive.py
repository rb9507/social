from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings
import io
import os

SCOPES = ['https://www.googleapis.com/auth/drive']

SERVICE_ACCOUNT_FILE = os.path.join(
    settings.BASE_DIR,
    'credentials.json'
)

FOLDER_ID = '1cg4gvKQLTeN5NzIbtJDDzib_x7p1Q1j8'

def upload_image_to_drive(django_file):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': django_file.name,
        'parents': [FOLDER_ID]
    }

    # Read file into memory
    file_stream = io.BytesIO(django_file.read())

    media = MediaIoBaseUpload(
        file_stream,
        mimetype=django_file.content_type,
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Reset pointer for Django reuse
    django_file.seek(0)

    file_id = file.get('id')

    # Make file public
    service.permissions().create(
        fileId=file_id,
        body={
            'type': 'anyone',
            'role': 'reader'
        }
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"
