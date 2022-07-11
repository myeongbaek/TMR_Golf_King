from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi
client = MongoClient('mongodb+srv://test:sparta@cluster0.pbhz9.mongodb.net/?retryWrites=true&w=majority', tlsCAFile= certifi.where())
db = client.dbsparta

import requests
from bs4 import BeautifulSoup

@app.route('/')
def home():
   return render_template('index.html')

@app.route("/score", methods=["POST"])
def movie_post():
    accessid_receive = request.form['accessid_give']
    date_receive = request.form['date_give']
    field_receive = request.form['field_give']
    score_receive = request.form['score_give']


    doc = {
        'accessid': accessid_receive,
        'date': date_receive,
        'field':field_receive,
        'score':score_receive
    }

    db.golf.insert_one(doc)

    return jsonify({'msg':'POST 연결 완료!'})

@app.route("/score", methods=["GET"])
def movie_get():
    score_list = list(db.golf.find({},{'_id':False}))
    return jsonify({'golfking':score_list})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True)