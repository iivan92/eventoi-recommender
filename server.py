"""Cloud Foundry"""
from flask import Flask
from flask import request
import os
import json

import collaborative as col
import content as con
import recommend as rec
import utils

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
    response = {}
    if num > 0:
        utils.create_events(num)

        response['code'] = 200
        response['data'] = "Created " + str(num) + " events"         
    else:        
        response['code'] = 500
        response['data'] = "The number of events to create must be larger than 0"

    return json.dumps(response)  

@app.route('/create/users/<int:num>', methods=['GET'])
def create_users(num):
    response = {}
    if num > 0:
        utils.create_users(num)

        response['code'] = 200
        response['data'] = "Created " + str(num) + " events"         
    else:        
        response['code'] = 500
        response['data'] = "The number of users to create must be larger than 0"
        
    return json.dumps(response)  

@app.route('/testing/init/<int:numUsers>/<int:numEvents>', methods=['GET'])
def init_testing(numUsers,numEvents):
    response = {}
    if numUsers > 0:
        utils.init_testing(numUsers,numEvents)

        response['code'] = 200
        response['data'] = "Testing init"         
    else:        
        response['code'] = 500
        response['data'] = "The parameters are incorrect"
        
    return json.dumps(response)  


@app.route('/testing')
def test():
    for i in [30,40,50]:
        for j in [20,40,60,80,100]:
            print "--------------------------------"
            print "  Test - Users: " + str(i) + " Events: " + str(j)
            print "--------------------------------"

            utils.init_testing(i,j)
            utils.compute_metric('cont')
            utils.compute_metric('col')
            
            print "--------------------------------"
    
    response = {}
    response['code'] = 200
    response['data'] = "Full Testing completed" 
        
    return json.dumps(response) 


@app.route('/testing/<method>', methods=['GET'])
def compute_testing(method):
    response = {}
    if method == "col" or method == "cont":
        utils.compute_metric(method)

        response['code'] = 200
        response['data'] = "Testing " + method         
    else:        
        response['code'] = 500
        response['data'] = "The method is incorrect"
        
    return json.dumps(response)  

@app.route('/update/con/all', methods=['PUT'])
def update_con_all():
    con.update_all()

    response = {}
    response['code'] = 200
    response['data'] = "Correct update"
    return json.dumps(response)   

@app.route('/update/con', methods=['PUT'])
def update_con():
    userId = request.form['userId']

    response = {}
    if userId is None: 
        response['code'] = 500
        response['data'] = "The user id has to be sent"
    else:
        con.update(userId)

        response['code'] = 200
        response['data'] = "Correct Update" 
    
    return json.dumps(response)

@app.route('/update/col', methods=['PUT'])
def update_col():    
    col.update()

    response = {}
    response['code'] = 200
    response['data'] = "Correct update"
    return json.dumps(response)    

@app.route('/recommend/<method>/<userId>', methods=['GET'])
def recommend(method,userId):    
    response = {}
    response['code'] = 200
    response['data'] = rec.recommend(method,userId)
    return json.dumps(response)   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)