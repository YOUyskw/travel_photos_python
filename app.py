from flask import Flask, request
from lib.grouping import main as grouping_image
from lib.image_feature import main as remove_duplicate_images

app = Flask(__name__)

@app.route('/health')
def home():
    return 'ok'

@app.route('/grouping', methods=['GET'])
def grouping():
    group_id = request.args.get('group_id')
    grouping_image(group_id)
    return "ok"
  
@app.route('/deduplicate', methods=['GET'])
def deduplicate():
    group_id = request.args.get('group_id')
    remove_duplicate_images(group_id)
    return "ok"