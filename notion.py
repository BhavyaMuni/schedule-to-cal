import asyncio
from pprint import pprint

# from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
import aiohttp


# TODO: CHANGE
async def get_assignments():
    async with aiohttp.ClientSession() as session:
        url = "https://api.notion.com/v1/databases"
        headers = {
            "Authorization": f"Bearer {os.getenv('NOTION-KEY')}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        payload = {
            "filter": {
                "property": "assignment",
                "select": {"is_not_empty": True},
            },
            "sorts": [{"property": "date", "direction": "ascending"}],
        }
        async with session.post(
            f"{url}/{os.getenv('NOTION-DATABASE-ID')}/query",
            headers=headers,
            json=payload,
        ) as resp:
            return await resp.json()


def auth():
    creds = Credentials(
        token=None,
        client_id=os.getenv("CLIENT-ID"),
        client_secret=os.getenv("CLIENT-SECRET"),
        refresh_token=os.getenv("REFRESH-TOKEN"),
        token_uri=os.getenv("TOKEN-URI"),
    )
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print("An error occurred: %s" % error)
    return None


# TODO: CHANGE
def create_event(start_time, end_time):
    return {
        "summary": "Starbucks",
        "location": "444 Yonge St, Toronto, ON M5B 2H4",
        "start": {
            "dateTime": start_time,
            "timeZone": "America/New_York",
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "America/New_York",
        },
        "reminders": {"useDefault": True},
    }


def get_names_and_dates(obj):
    for i in obj["results"]:
        pprint(
            (
                i["properties"]["lecture/assignment"]["title"][0]["plain_text"],
                # i["properties"][],
                i["properties"]["date"]["date"]["start"],
            )
        )


async def main():
    assignments = await get_assignments()
    get_names_and_dates(assignments)
    # pprint(assignments)
    # with auth() as service:
    #     for i in shifts:
    #         if i["DailySeconds"] > 0:
    #             s, e = get_times(i["DailyShift"][0], i["StartDate"])
    #             event = create_event(s, e)
    #             event = (
    #                 service.events()
    #                 .insert(calendarId=os.getenv("CALENDAR-ID"), body=event)
    #                 .execute()
    #             )
    #             print("Event created: %s" % (event.get("htmlLink")))


if __name__ == "__main__":
    try:
        load_dotenv()
    except:
        pass
    asyncio.run(main())
