import requests
import pymongo
from bson.objectid import ObjectId
import operator
import datetime
import random
import numpy as np
from math import*
import time
import utils

MONGODB_URI = 'mongodb://admin:admin1234@ds013881.mlab.com:13881/db-eventoi-dev'

def update(userId):
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()
    
    users   = db['users']
    events  = db['events']
    content = db['cont']

    userId = str(userId)
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

                content.update({'user': userId}, {"$set": rowPred}, upsert=True)
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

                rowPred = {'user':userId,'data':utils.normalize(result)}
                
                content.update({'user': userId}, {"$set": rowPred}, upsert=True)
        else:
            cursorE = events.find()

            result = [{'id':str(cursorE[x]['_id']),'value':0} for x in xrange(cursorE.count())]
            rowPred = {'user':userId,'data':result}
            
            content.update({'user': userId}, {"$set": rowPred}, upsert=True)

def update_all():
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()
    
    users   = db['users']

    cursor = users.find({}, {"_id":1})

    for user in cursor:
        update(user['_id'])

def getSortAtr(item):
    return item['value']
