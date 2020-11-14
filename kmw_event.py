import datetime
import json
import logging
import pprint
import requests
import sys
import time

##################################################################
# This script was created to monitor mypthub.net for
# particular classes and then enroll in them automatically
# so that you do not have to constantly check the site
# and possibly end up on the wait list.
#
# USAGE:
# Run the script about 24 hours prior to the start of the class.
# The script will login to mypthub.net and get an access token,
# which will be used for:
# 1. checking the calendar for the class
# 2. getting credit information
# 3. enrolling in the class
#
# If all goes well, then you will recieve a confirmation e-mail
# for enrolling in he class from mypthub.net.
#
# DEBUGGING:
# A log file will be created called kmw_event.log.  This file will
# be in the same directory as this script.
#
# TODO:
# 1. Check if there are sufficient credits
# 2. Use latest credit record if multiple credit records exists.
#    Easy fix. Just reference last record: credit_data[-1]
##################################################################

USER_NAME = 'PUT YOUR USERNAME HERE'
PASSWORD = 'PUT YOUR PASSWORD HERE'

STRENGTH_AND_CONDITIONING_WESTLA = 'Strength and Conditioning (West LA Outdoors - Parking Structure)'
START_TIMES = ['T17:00:00', 'T18:00:00']

class MyPTHub:
    def __init__(self):
        self.logger = logging.getLogger('MyPTHub')
        self.f_handler = logging.FileHandler('kmw_event.log')
        self.f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.f_handler.setFormatter(self.f_format)
        self.logger.addHandler(self.f_handler)
        self.logger.setLevel(logging.INFO)

        self.access_token = ''
        self.current_user = dict()
        self.event_data = dict()
        self.credit_data = dict()
        self.booking_data = dict()
        
    #########################################
    # Login to mypthub.net
    #########################################
    def login(self, user_name, password):
        headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'
            }
            
        payload = {
            'username' : user_name,
            'password' : password
            }

        response = requests.post('https://api.mypthub.net/v4/auth/token', headers=headers, data=payload)
        if response.status_code == 200:
            self.access_token = json.loads(response.text)['access_token']
            self.logger.info('Logged into mypthub.net')
            self.logger.warning('testing')
            self.logger.error('testing')
            return True
            
        self.logger.error('Failed to login to mypthub.net. status_code = ' + str(response.status_code))
        return False
        
    #########################################
    # Look up the event
    #########################################        
    def lookup_event(self, event_name, event_times, start_date, end_date):
        def is_event(event, event_name, event_times):
            if event['title'] == event_name:
                for et in event_times:
                    if event['start'].startswith(et):
                        return True
            return False
            
        headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Language' : 'en',
            'Accept-Encoding' : 'gzip, deflate',
            'Authorization' : 'Bearer ' + self.access_token
            }
            
        params = {
            'startDate' : start_date,
            'endDate' : end_date,
            'type' : 'company'
            }
            
        response = requests.get('https://api.mypthub.net/v4/calendar-event-times', headers=headers, params=params)
        if response.status_code == 200:
            events = json.loads(response.text)
            self.current_user = events['currentUser']
            for event in events['events']:
                event = dict(event)
                if is_event(event, event_name, event_times):
                    self.event_data = event
                    self.logger.info('EVENT:\n' + pprint.pformat(self.event_data))
                    return True
                    
        self.logger.warning('Event not found. status_code = ' + str(response.status_code))
        return False
        
    #########################################
    # Get credit info
    #########################################
    def get_credits(self):
        headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Language' : 'en',
            'Accept-Encoding' : 'gzip, deflate',
            'Authorization' : 'Bearer ' + self.access_token,
            'Content-Type' : 'application/json'
            }
            
        params = {
            'attending_trainers' : self.event_data['attending_trainer_ids'][0],
            'credit_cost' : self.event_data['credit_cost'],
            'event_id' : self.event_data['event_id']
            }
            
        response = requests.get('https://api.mypthub.net/v4/package-credits/event-trainers', headers=headers, params=params)
        if response.status_code == 200:
            self.credit_data = json.loads(response.text)['credits']
            self.logger.info('CREDITS:\n' + pprint.pformat(self.credit_data))
            return True
            
        self.logger.error('Credit data not found. status_code = ' + str(response.status_code))
        return False
        
    #########################################
    # Enroll in the event
    #########################################
    def enroll_event(self):           
        headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Language' : 'en',
            'Accept-Encoding' : 'gzip, deflate',
            'Authorization' : 'Bearer ' + self.access_token,
            'Content-Type' : 'application/json'
            }
            
        payload = {
            'calendar_event_id' : self.event_data['event_id'],
            'calendar_event_time_id' : self.event_data['event_time_id'],
            'credit_id' : self.credit_data[0]['id'], # this currently works for me, but might need to change if more elements are added
            'customer_id' : self.current_user['customer_id'],
            'date' : self.event_data['original_date']
            }
        
        event_id = str(self.event_data['event_id'])
        
        response = requests.post('https://api.mypthub.net/v4/calendar-events/' + event_id + '/book', headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            self.booking_data = json.loads(response.text)
            self.logger.info('BOOKING:\n' + pprint.pformat(self.booking_data))
            return True
            
        self.logger.error('Failed to enroll. status_code = ' + str(response.status_code))
        return False
        
def main():
    pt = MyPTHub()
    if not pt.login(USER_NAME, PASSWORD):
        return 1
        
    start_date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.today() + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    start_times = [start_date + st for st in START_TIMES]
    
    event_found = False
    while not event_found:
        event_found = pt.lookup_event(STRENGTH_AND_CONDITIONING_WESTLA, start_times, start_date, end_date)
        if not event_found:
            time.sleep(60)
        
    if event_found:
        if not pt.enroll_event():
            return 1
        
    return 0
        
if __name__ == '__main__':
    sys.exit(main())
