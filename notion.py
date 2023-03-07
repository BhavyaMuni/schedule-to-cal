import asyncio
import os

import aiohttp
from dotenv import load_dotenv

# from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
            "sorts": [{"property": "Due Date", "direction": "ascending"}],
        }
        async with session.post(
            f"{url}/{os.getenv('NOTION-DATABASE-ID')}/query",
            headers=headers,
            json=payload,
        ) as resp:
            return await resp.json()


async def get_course_names(id):
    async with aiohttp.ClientSession() as sess:
        url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {os.getenv('NOTION-KEY')}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        async with sess.get(f"{url}/{id}", headers=headers) as resp:
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


def create_event(event, course, date):
    return {
        "summary": f"{course} - {event}",
        "start": {
            "date": date,
            "timeZone": "America/New_York",
        },
        "end": {
            "date": date,
            "timeZone": "America/New_York",
        },
        "reminders": {"useDefault": True},
    }


async def get_names_and_dates(obj):
    final_out = []
    courses = set(
        i["properties"]["Course"]["relation"][0]["id"] for i in obj["results"]
    )
    course_names = {}
    for i in courses:
        course_names[i] = (await get_course_names(i))["properties"]["Course Code"][
            "rich_text"
        ][0]["text"]["content"]

    for i in obj["results"]:
        final_out.append(
            (
                i["properties"]["Assignment"]["title"][0]["plain_text"],
                course_names[i["properties"]["Course"]["relation"][0]["id"]],
                i["properties"]["Due Date"]["date"]["start"],
            )
        )
    return final_out


async def main():
    assignments = await get_assignments()
    # course = await get_course_names("8da46137-24ac-4672-bcc0-9322f7e34473")
    all_assignments = await get_names_and_dates(assignments)

    with auth() as service:
        for i in all_assignments:
            event = create_event(i[0], i[1], i[2])
            event = (
                service.events()
                .insert(calendarId=os.getenv("NOTION-CALENDAR-ID"), body=event)
                .execute()
            )
            print("Event created: %s" % (event.get("htmlLink")))


if __name__ == "__main__":
    try:
        load_dotenv()
    except Exception as _:
        pass
    asyncio.run(main())
