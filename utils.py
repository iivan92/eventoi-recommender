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
import collaborative as col
import content as con

MONGODB_URI = 'mongodb://admin:admin1234@ds013881.mlab.com:13881/db-eventoi-dev'

def create_events(num):
    template = {  "published": True,
                  "suspended": False,
                  "currency": "EUR",
                  "hostName": "Ivan Megias",
                  "hostFb": "10206104050992562",                  
                  "host": "5736163851e4201d00df0569",
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

    eventsDB = db['events']
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

    eventsDB.insert(returnEvents) 

def create_users(num):
    template = {    "gender": "male",
                    "tickets": [],
                    "favouriteEvents": [],
                    "likes": []
                };    

    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()

    usersDB = db['users']
    eventsDB = db['events']
    
    listE = list(eventsDB.find({}, {"_id":1}))
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

    usersDB.insert(returnUsers)

def normalize(vector):
    max1 = vector[0]['value']
    max2 = fabs(vector[len(vector)-1]['value'])
    maxPred = max(max1,max2)

    if maxPred == 0:
        maxPred = 1

    return [{'id':pred['id'],'value':pred['value']/maxPred} for pred in vector]

def init_testing(numUsers,numEvents):
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()

    usersDB   = db['users']
    eventsDB  = db['events']
    contDB    = db['cont']
    colDB     = db['col']

    usersDB.remove()
    eventsDB.remove()
    contDB.remove()
    colDB.remove()

    create_events(numEvents)
    create_users(numUsers)

def compute_metric(alg):
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()

    usersDB   = db['users']
    eventsDB  = db['events']
    algDB     = db[alg]

    if alg == "col":
        col.update()
    else:
        con.update_all()
    
    users = usersDB.find()
    
    RMSE = 0
    MAE = 0
    n = 0
    for user in users:
        likes = user['likes']

        userId = str(user['_id'])

        cursor    = algDB.find({'user':userId})
        predAlg   = cursor[0]['data'];
        listId    = [pred['id'] for pred in predAlg]

        if len(likes) > 0:
            for like in likes:
                eventId = str(like['eventId'])
                value = like['value']

                idx = listId.index(eventId)
                valueAlg = predAlg[idx]['value']

                RMSE = RMSE + (valueAlg - value) ** 2
                MAE = MAE + fabs(valueAlg - value)

                n = n + 1

    RMSE = sqrt(RMSE / n)
    MAE = MAE / n

    print "(" + alg + ") - RMSE = " + str(RMSE) + " MAE = " + str(MAE)
