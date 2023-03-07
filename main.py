# import json
import asyncio

# from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

from dotenv import load_dotenv
import aiohttp
import json
from typing import List, Optional, Dict, Any

load_dotenv()


async def get_shifts() -> List:
    async with aiohttp.ClientSession() as session:
        url = "https://myschedule.metro.ca/api/"
        await session.get(f"{url}Login/{os.getenv('METRO-LOGIN')}")
        async with session.get(f"{url}Employee/") as data:
            return (await data.json())["WorkTime"][-7:]


def auth() -> Optional[Any]:
    sacc = json.loads(str(os.getenv("SERVICE-ACCOUNT")))

    service_account = Credentials.from_service_account_info(sacc)

    try:
        service = build("calendar", "v3", credentials=service_account)
        return service
    except HttpError as error:
        print("An error occurred: %s" % error)
    return None


def create_event(start_time, end_time) -> Dict:
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


def get_times(time, date) -> tuple[str, str]:
    time_s = time.split("-")[0] + ":00"
    time_e = time.split("-")[1].split(" ")[0] + ":00"
    start_time = date[: -len(time_s)] + time_s
    end_time = date[: -len(time_e)] + time_e
    return (start_time, end_time)


async def main() -> None:
    shifts: List = await get_shifts()
    with auth() as service:
        for i in shifts:
            if i["DailySeconds"] > 0:
                s, e = get_times(i["DailyShift"][0], i["StartDate"])
                event = create_event(s, e)
                event = (
                    service.events()
                    .insert(calendarId=os.getenv("CALENDAR-ID"), body=event)
                    .execute()
                )
                print("Event created: %s" % (event.get("htmlLink")))


if __name__ == "__main__":
    asyncio.run(main())
