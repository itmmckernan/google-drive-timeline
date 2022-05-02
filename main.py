
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import plotly.express as px
from alive_progress import alive_bar
from datetime import datetime, timedelta
import pandas as pd


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
    df = pd.DataFrame(columns=('name', 'start', 'end', 'link'))
    try:
        service = build('drive', 'v3', credentials=creds)
        num = 10000
        pageToken = None
        with alive_bar(num) as bar:
            for i in range(int(num/1000)):
                # Call the Drive v3 API
                results = service.files().list(
                    q="'itmmckernan@gmail.com' in owners",
                    pageSize=1000, fields="nextPageToken, files(name, webViewLink, createdTime, modifiedTime)", pageToken=pageToken).execute()
                items = results.get('files', [])
                pageToken = results.get('nextPageToken')

                if not items:
                    print('No files found.')
                    return

                for item in items:
                    bar()
                    fmt_string = '%Y-%m-%dT%H:%M:%S.'
                    createdTime = datetime.strptime(item['createdTime'][:-4], fmt_string)
                    modifiedTime = datetime.strptime(item['modifiedTime'][:-4], fmt_string)


                    df = df.append(dict(name=item['name'], start=createdTime, end=modifiedTime, link=item['webViewLink']), ignore_index=True)
                    print(item)

    except HttpError as error:
         print(f'An error occurred: {error}')
    df.to_pickle('out.pkl')
    fig = px.timeline(df, x_start="start", x_end="end", y="name")
    fig.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    fig.show()


if __name__ == '__main__':
    main()