from flask import Flask, request
from lib.grouping import grouping_image
from lib.image_feature import main as remove_duplicate_images
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Firestore への接続 -----------------
KEY_PATH = '.env/trip-timeline-28131-firebase-adminsdk-u4wq6-6d1ede5eda.json'
cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred)
# db = firestore.client()
# -----------------------------------

@app.route('/health')
def home():
    return 'ok'

@app.route('/grouping', methods=['GET'])
def grouping():
    group_id = request.args.get('group_id')
    print(f"grouping start (group_id: {group_id})")
    grouping_image(group_id)
    print(f"grouping end (group_id: {group_id})")
    
    return "ok"
  
@app.route('/deduplicate', methods=['GET'])
def deduplicate():
    group_id = request.args.get('group_id')
    print(f"deduplication start (group_id: {group_id})")
    remove_duplicate_images(group_id)
    print(f"deduplication end (group_id: {group_id})")
    return "ok"
  
