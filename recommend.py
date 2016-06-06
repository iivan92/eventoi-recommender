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

def recommend(method,userId):   
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()
    prediction = db[method]

    cursor = prediction.find({'user':userId});

    if cursor.count() > 0:
        data = cursor[0]['data']
        listRec = []

        if len(data) > 0:
            i = 0
            for rec in data:
                if i == 30: 
                    return listRec
                if rec['value'] >= 0: 
                    listRec.append(str(rec['id']))
                    i = i + 1
                else:   
                    return listRec

        return []
    else:
        return []
