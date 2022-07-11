from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi
client = MongoClient('mongodb+srv://test:sparta@cluster0.pbhz9.mongodb.net/?retryWrites=true&w=majority', tlsCAFile= certifi.where())
db = client.dbsparta

@app.route('/')
def home():
   return render_template('main.html')

@app.route("/golf", methods=["POST"])
def movie_post():
    accessid_receive = request.form['accessid_give']
    date_receive = request.form['date_give']
    field_receive = request.form['field_give']
    score_receive = request.form['score_give']


    doc = {
        'accessid': accessid_receive,
        'date': date_receive,
        'field': field_receive,
        'score': score_receive
    }

    db.golf_scores.insert_one(doc)

    return jsonify({'msg': 'POST 연결 완료!'})

@app.route("/golf", methods=["GET"])
def movie_get():
    score_list = list(db.golf_scores.find({}, {'_id': False}))
    return jsonify({'golf_scores': score_list})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True)
