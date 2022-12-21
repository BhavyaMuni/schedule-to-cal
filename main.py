# import json
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
import aiohttp

# from typing import *

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

load_dotenv()


async def get_shifts():
    async with aiohttp.ClientSession() as session:
        url = "https://myschedule.metro.ca/api/"
        await session.get(f"{url}Login/{os.getenv('METRO-LOGIN')}")
        async with session.get(f"{url}Employee/") as data:
            json_data = await data.json()
            shifts = json_data["WorkTime"]
        return shifts


def auth():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print("An error occurred: %s" % error)


async def main():
    shifts = await get_shifts()
    for i in shifts:
        print(i)


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(main())
