import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']

"""def create_folder(folder_name):

    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    credentials = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=credentials)

    folder_metadata = {
        'name': folder_name,
        'mimeType':'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=folder_metadata).execute()

    return folder"""
def credentials_check():

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds
def upload_pdf(pdf_writer, file_name):

    credentials = credentials_check()

    service = build('drive', 'v3', credentials=credentials)

    file_stream = io.BytesIO()

    pdf_writer.write(file_stream)
    file_stream.seek(0)

    file_metadata = {
        'name': file_name,
    }

    file_data = MediaIoBaseUpload(file_stream, mimetype='application/pdf')

    file = service.files().create(body=file_metadata, media_body=file_data, fields='id').execute()

    print(f'PDF uploaded. ID: {file["id"]}')



