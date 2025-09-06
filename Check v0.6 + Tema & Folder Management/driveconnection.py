import datetime
import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.metadata.readonly']

def create_folder(folder_name, folder_parent, service):
    start = datetime.datetime.now()

    folder_metadata = {
        'name': folder_name,
        'mimeType':'application/vnd.google-apps.folder',
        'parents' : [folder_parent["id"]]
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()

    print(f"Folder Created. id: {folder['id']}")
    print(f"Time to create folder = {datetime.datetime.now() - start}")

    return folder

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

def service_building():
    credentials = credentials_check()
    service = build('drive', 'v3', credentials=credentials)
    return service

def upload_pdf(pdf_writer, file_name, service, folder):

    file_stream = io.BytesIO()

    pdf_writer.write(file_stream)
    file_stream.seek(0)

    file_metadata = {
        'name': file_name,
        'parents': [folder["id"]]
    }

    file_data = MediaIoBaseUpload(file_stream, mimetype='application/pdf')

    file = service.files().create(body=file_metadata, media_body=file_data, fields='id').execute()

    print(f'PDF uploaded. ID: {file["id"]}')

def search_folder(folder_name, service):
    start = datetime.datetime.now()
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])

    print(f"Time Searching Folder: {datetime.datetime.now() - start}")
    if folders:
        for folder in folders:
            print(f"Folder Name: {folder['name']}, ID: {folder['id']}")
            return folder
    else:
        return None
