"""Cloud Foundry test"""
from flask import Flask
from flask import request
import os
import json
import requests
import pymongo
from bson.objectid import ObjectId
import operator
import datetime
import random
import numpy as np

MONGODB_URI = 'mongodb://admin:admin1234@ds013881.mlab.com:13881/db-eventoi-dev'

app = Flask(__name__)

# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))

app.config.update(
    DEBUG=True,
)

app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def welcome():
    return 'Welcome to flask on Bluemix.'

@app.route('/create/events/<int:num>', methods=['GET'])
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

    table = db['table']

    cursor = table.find({'event':'df'})
    if cursor.count() == 0:
        counter = [0 for x in xrange(8)]
    else:  
        counter = cursor[0]['data']
        
    for event in returnEvents:
        listServices = event['services']

        for service in listServices:
            counter[service] = counter[service] + 1

    rowC = {'event': 'df', 'data': counter}
    table.update({'event': 'df'}, {"$set": rowC}, upsert=True)

    response = {}
    response['code'] = 200
    response['data'] = "Created " + str(num) + " events"
    return json.dumps(response)    

@app.route('/create/users/<int:num>', methods=['GET'])
def create_users(num):
    return str(num)

@app.route('/create/user/<userId>/likes/<int:num>', methods=['GET'])
def create_likes(userId,num):
    return userId + " " + str(num)

def updateByUser(userId):
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()

    table = db['table']
    users = db['users']
    events = db['events']

    objectUID = ObjectId(userId)

    cursor = users.find({'_id': objectUID})
    if cursor.count()>0:
        user = cursor[0]
        if 'likes' in user:
            likes = user['likes']

            if len(likes)==0: 
                cursorE = events.find()

                result = [{'id':str(cursorE[x]['_id']),'value':0} for x in xrange(cursorE.count())]
                rowPred = {'user':userId,'data':result}

                prediction = db['prediction']
                prediction.update({'user': userId}, {"$set": rowPred}, upsert=True)
            else:
                zeros2 = [0 for x in xrange(8)]
                for like in likes:
                    eventId = like['eventId']
                    value = like['value']

                    objectUID = ObjectId(eventId)

                    cursor = events.find({'_id':objectUID})
                    if cursor.count() > 0:
                        services = cursor[0]['services']

                        for service in services:
                            zeros2[service] = zeros2[service] + value

                result = []
                cursor = events.find()
                for row in cursor:
                    services = row['services']

                    predict = 0
                    for service in services:
                        predict = predict + zeros2[service]

                    #if predict >= 0:
                    result.append({'id':str(row['_id']),'value':predict})

                result.sort(key=getSortAtr,reverse=True)

                rowPred = {'user':userId,'data':result}

                prediction = db['prediction']
                prediction.update({'user': userId}, {"$set": rowPred}, upsert=True)
        else:
            cursorE = events.find()

            result = [{'id':str(cursorE[x]['_id']),'value':0} for x in xrange(cursorE.count())]
            rowPred = {'user':userId,'data':result}

            prediction = db['prediction']
            prediction.update({'user': userId}, {"$set": rowPred}, upsert=True)


@app.route('/insert', methods=['POST'])
def insert():
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()
    table = db['table']

    cursor = table.find({'event':'df'})
    if cursor.count() == 0:
        counter = [0 for x in xrange(8)]
    else:  
        counter = cursor[0]['data']
    
    listServices = eval(request.form.get('services'))
    
    for service in listServices:
        counter[service] = counter[service] + 1
    
    rowC = {'event': 'df', 'data': counter}
    
    table.update({'event': 'df'}, {"$set": rowC}, upsert=True)

    updateByUser(request.form.get('userId'))

    response = {}
    response['code'] = 200
    response['data'] = "Correct Insert"
    return json.dumps(response)

def getSortAtr(item):
    return item['value']

@app.route('/update', methods=['PUT'])
def update():
    updateByUser(request.form['userId'])

    response = {}
    response['code'] = 200
    response['data'] = "Correct Update"
    return json.dumps(response)

@app.route('/recommend/<userId>', methods=['GET'])
def recommend(userId):    
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()
    prediction = db['prediction']

    cursor = prediction.find({'user':userId});

    if cursor.count() > 0:
        response = {}
        response['code'] = 200
        response['data'] = []

        data = cursor[0]['data']

        if len(data) > 0:
            i = 0
            for rec in data:
                if i == 30: 
                    return json.dumps(response)
                if rec['value'] >= 0: 
                    response['data'].append(str(rec['id']))
                    i = i + 1
                else:   
                    return json.dumps(response)

        return json.dumps(response)
    else:
        return ""



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)