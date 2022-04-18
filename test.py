import requests
import time
from twilio.rest import Client
import logging
import datetime as dt
# import beepy as beep

logging.basicConfig(
    filename='vaccine.log',
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("twilio").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Twilio Config: fill these
account_sid = ''
auth_token = ''
# Phone number from twilio dashboard with area code
twilio_phone_no = ''
district_id = '395'  # For Mumbai
# Fill 10 digit phone number
phone_numbers = ['', '']

# JWT Token for cowin
TOKEN = ''


headers = {
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}

url = f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={district_id}&date='


def init_dates():
    day = dt.date.today() + dt.timedelta(days=0)
    dates = []
    for _ in range(1):
        dates.append(day.strftime('%d-%m-%Y'))
        day = day + dt.timedelta(days=7)
    return dates
    # return ['08-05-2021']


def make_sound():
    # beep.beep(1)
    pass


def send_text_message(phone_nos, center, date, av_cap):
    body = 'New vaccination center with 18+ found: ' + center['name'] + ' ' + center['block_name'] + ' ' + str(
        center['pincode']) + ' ' + date + '\nAvailable Capacity: ' + str(av_cap)
    logger.info(f'Sending message with body: {body}')
    send_text_message_with_body(phone_nos, body)


def send_text_message_with_body(phone_nos, body):
    client = Client(account_sid, auth_token)
    print(body)
    for phone_no in phone_nos:
        message = client.messages.create(
            body=body,
            from_=twilio_phone_no,
            to=f'{phone_no}'
        )


def schedule_appointment(session_id, center_id, slots):
    params = {
        "dose": 1,
        "session_id": session_id,
        "center_id": center_id,
        "slot": slots[0],
        "beneficiaries": ["[BENEFICIARY_ID]"]
    }

    print(params)

    url = 'https://cdn-api.co-vin.in/api/v2/appointment/schedule'
    r = requests.post(url, json=params, headers=headers)
    print(r.status_code)
    print(r.json())
    if r.status_code / 100 == 2:
        # beep.beep(6)
        send_text_message_with_body(
            phone_numbers, 'Booked Appointment successfully!')
        print('Booked appointment, exiting...')
        exit()


while (True):
    dates = init_dates()
    logger.info('Checking...')
    for date in dates:
        print(f'Checking for date: {date}')
        try:
            r = requests.get(url + date, headers=headers)
            for center in r.json()['centers']:
                for session in center['sessions']:
                    if session['available_capacity'] > 0:
                        print('Found center: ', center)
                        logger.info(f'Found center: {str(center)}')
                        make_sound()
                        print('Attempting to schedule appointment...')
                        cname = center['name'].lower()
                        # Vaccination center preferences here
                        if 'kohinoor' in cname:
                            # schedule_appointment(session['session_id'], center['center_id'], session['slots'])
                            send_text_message(
                                phone_numbers, center, session['date'], session['available_capacity'])
            time.sleep(1)
            print(f'Done checking for date: {date}')
        except:
            print('Error encountered, retrying in 0.5 seconds...')
            logger.error('Error encountered, retrying in 0.5 seconds...')
            time.sleep(0.5)
    print(f'Waiting for 10 seconds...')
    logger.info(f'Waiting for 10 seconds...')
    time.sleep(10)
