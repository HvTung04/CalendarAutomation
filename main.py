import os.path
import datetime as dt

from google.auth.transport.requests import Request 
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def create_events():
    events = []
    print("How many subjects you gonna have in this semester?")

    # Loop for n times which n is the number of subjects user input
    for i in range(int(input())):
        print(f"Setting up for subject no.{i+1} ...")
        summary = input("Enter class's name: ")
        location = input("Enter class's location / lecture hall: ")
        description = input("Enter class's description: ")

        # Construct start dateTime
        date = input("Enter class's date (YYYY-MM-DD): ")
        startTime = input("Enter class's start time (hh:mm:ss): ")
        start = {
            'dateTime': date + 'T' + startTime + "+07:00",
            'timeZone': 'Asia/Bangkok',
        }

        # Construct end dateTime
        endTime = input("Enter class's end time (hh:mm:ss): ")
        end = {
            'dateTime': date + 'T' + endTime + "+07:00",
            'timeZone': 'Asia/Bangkok',
        }
        repeat = input("How many weeks do you want this subject to repeat: ")
        recurrence = ['RRULE:FREQ=WEEKLY;COUNT='+repeat]
        attendees = []
        
        if input("Do you want to add your friend to this class? ").lower().startswith('y'):
            loop = int(input("How many friends you want to add? "))
            for i in range(loop):
                attendees.append(
                    {'email' : input("Enter your friend email: ")}
                )
        
        reminders = {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        }
        if input("Do you want to add reminder for this class? ").lower().startswith('y'):
            method = 0 if input('Choose method: email or popup. ').lower() == 'email' else 1
            time = int(input('Choose time for reminder (minutes): '))
            reminders['overrides'][method]['minutes'] = time
        
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': start,
            'end': end,
            'recurrence': recurrence,
            'attendees': attendees,
            'reminders': reminders,
        }
        events.append(event)

    return events

def main():
    creds = None

    if os.path.exists("token.json"): # Auth -> create Token -> Reuse token everytime >< If not exist create
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If there are no (valid) creds available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else: # Create first time
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
    
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)

        eventsList = create_events()
        for idx, event in enumerate(eventsList):
            event = service.events().insert(calendarId="primary", body=event).execute()
            print(f"Subject no.{idx+1} added, link: {event.get('htmlLink')}.")

    except HttpError as error:
        print("An error occured:", error)


if __name__ == "__main__":
    main()