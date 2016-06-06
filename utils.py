import json
import requests
import pymongo
from bson.objectid import ObjectId
import operator
import datetime
import random
import numpy as np
from math import*
import time

MONGODB_URI = 'mongodb://admin:admin1234@ds013881.mlab.com:13881/db-eventoi-dev'

def create_events(num):
    template = {  "published": True,
                  "suspended": False,
                  "currency": "EUR",
                  "hostName": "Mary Poppins",
                  "hostFb": "117318205316818",                  
                  "host": "5735088f8b73191d00cf365f",
                  "visibleAssistants": True,
                  "isFree": True,
                  "sharing": 1,
                  "visibility": 0,
                  "countryISO": "ES",
                  "coordinates": [
                    1.38506389999999,
                    2.173403
                  ],
                  "city": "Barcelona, Spain",
                  "location": "Barcelona, Spain",                                    
                  "cancPolicy": 0,
                  "capacity": 32,
                  "deposit": 0,
                  "simplePrice": 0,
                  "ticketPrice": 0,                  
                  "duration": 120,
                  "limit": 1440,                                    
                  "rules": "",
                  "assistants": [],
                  "progress": []
            };    

    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()

    events = db['events']
    returnEvents = []

    for i in xrange(num):
        event = template.copy()
        event['name'] = "Event created #" + str(i)
        event['description'] = "This event #" + str(i) + " have been created to test the recommender."

        day = random.randint(1, 28)
        month = random.randint(1, 12)
        year = 2016 + random.randint(0, 2)
        hour = random.randint(1, 23)
        minute = random.randint(1, 59)        
        
        d = datetime.datetime(year, month, day, hour, minute, 0)
        
        event['date'] = '{:%Y-%m-%dT%H:%M:%S.000Z}'.format(d)

        randMax = random.randint(1, 4)
        event['services'] = []

        for j in xrange(randMax):
            value = random.randint(0, 7)
            while value in event['services']:
                value = random.randint(0, 7)
            event['services'].append(value)   

        returnEvents.append(event)        

    events.insert(returnEvents) 

def create_users(num):
    template = {    "gender": "male",
                    "tickets": [],
                    "favouriteEvents": [],
                    "likes": []
                };    

    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()

    users = db['users']
    events = db['events']
    
    listE = list(events.find({}, {"_id":1}))
    countE = len(listE)

    returnUsers = []

    for i in xrange(num):
        userdate = time.strftime("%d%m%Y");
        user = template.copy()
        user['name'] = "User " + str(i) + " Test " + userdate
        user['email'] = "user-" + userdate + "-" + str(i) + "@test.com"
        user['likes'] = []

        randMax = random.randint(2, countE/2)
        likes = []
        for j in xrange(randMax):
            idx = random.randint(0, countE-1)
            while idx in likes:
                idx = random.randint(0, countE-1)
            likes.append(idx) 

            value = random.randint(0, 1)
            if value == 0:
                value = -1

            user['likes'].append({"eventId": str(listE[idx]["_id"]), "value": value})  

        returnUsers.append(user)        

    users.insert(returnUsers)
