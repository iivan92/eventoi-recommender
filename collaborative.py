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

def update():
    updateNeig(25)

def updateNeig(numNeig):    
    client = pymongo.MongoClient(MONGODB_URI)

    db = client.get_default_database()

    users           = db['users']
    events          = db['events']
    collaborative   = db['col']

    listEvents  = list(events.find({}, {"_id":1}))
    listUsers   = list(users.find())
    numEvents   = len(listEvents)
    numUsers    = len(listUsers)

    matrix = compute_matrix(listUsers, listEvents)

    matrixUsers = compute_matrix_sim(matrix,numUsers)

    sim = []
    for i in xrange(numUsers):
        userId = str(listUsers[i]['_id'])
        result = [{'id':str(listUsers[x]['_id']),'pos':x,  'value':matrixUsers[i][x]} for x in xrange(numUsers)]
        sim.append({'id':userId,'list':result})

    matrixPred = compute_matrix_pred(sim,matrix,numUsers,numEvents,numNeig)
     
    for i in xrange(numUsers):
        userId = str(listUsers[i]['_id'])
        result = [{'id':str(listEvents[x]['_id']),'value':matrixPred[i][x]} for x in xrange(numEvents)]
        result.sort(key=getSortAtr,reverse=True)

        userPredict = {'user':userId,'data':utils.normalize(result)}        
        
        collaborative.update({'user': userId}, {"$set": userPredict}, upsert=True)

def getSortAtr(item):
    return item['value']

def compute_matrix(listUsers,listEvents):
    numUsers = len(listUsers)
    numEvents = len(listEvents)

    matrix = np.zeros((numUsers,numEvents))
    
    for i in xrange(numUsers):
        user = listUsers[i]
    
        if 'likes' in user:
            likes = user['likes']
            for like in likes:
                eventId = like['eventId']
                value = like['value']
                idx = listEvents.index({"_id":ObjectId(eventId)})

                matrix[i][idx] = value

    return matrix

#interesect but penalizing the differences
def simple_similarity(x,y):
    count = 0
    for i in xrange(len(x)):
        count = count + (x[i]*y[i])

    return count

def coef(v1,v2):
    newv1 = []
    newv2 = []

    union = 0
    for i in xrange(len(v1)):
        if v1[i] != 0 or v2[i] != 0:
            union = union + 1
        if v1[i] != 0 and v2[i] != 0:
            newv1.append(v1[i])
            newv2.append(v2[i])

    v1 = np.array(newv1)
    v2 = np.array(newv2)

    #If v1 and v2 don't have score the same item
    if len(v1)==0:
        return 0

    return simple_similarity(v1,v2)/union

def compute_matrix_sim(matrix,numUsers):
    matrixUsers = np.zeros((numUsers,numUsers))

    for i in xrange(numUsers):
        for j in range(i+1, numUsers):            
            matrixUsers[i][j] = coef(matrix[i],matrix[j])
            matrixUsers[j][i] = matrixUsers[i][j]

    return matrixUsers

def getNeighbors(corr,numNeig):    
    final = list(corr)
    final.sort(key=getSortAtr,reverse=True)

    if numNeig > len(final):
        numNeig = len(final)/2

    return final[:numNeig]

def compute_matrix_pred(corr,matrix,numUsers,numEvents,numNeig):    
    matrixPred = np.zeros((numUsers,numEvents))
    for i in xrange(numUsers):
        listNeigh = getNeighbors(corr[i]['list'],numNeig)
        
        for event in xrange(numEvents):
            dot = 0
            weight = 0
            for neigh in listNeigh:
                c = neigh['value']
                pos = neigh['pos']

                value = matrix[pos][event]

                dot = dot + value * c

                if value != 0:
                    weight = weight + c
            
            if weight != 0:
                matrixPred[i][event] = dot / weight

    return matrixPred
