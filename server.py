from flask import Flask,request,jsonify
import pymongo
import datetime
from dotenv import load_dotenv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
load_dotenv()

# MongoDB
client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['mydatabase']
collection = db['events']

@app.route('/')
def home():
    return 'Welcome'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')

        if event_type == 'push':
            author = data['pusher']['name']
            branch = data['ref'].split('/')(-1)
            timeStamp = datetime.datetime.now()
            event = {
                "type" : "push",
                "author" : author,
                "branch":branch,
                "timeStamp":timeStamp
            }
        
        elif event_type == 'pull_request':
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timeStamp = datetime.datetime.now()
            event = {
                "type" : "pull_request",
                "author" : author,
                "from_branch":from_branch,
                "to_branch":to_branch,
                "timeStamp":timeStamp
            }

        collection.insert_one(event)
        return 'WebHook Recieved', 200

@app.route('/events',methods=['GET'])
def events():
    events = list(collection.find().sort('timeStamp',-1))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)    

if __name__ == '__main__':
    app.run(port=5000)