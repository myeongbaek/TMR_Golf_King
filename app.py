import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
# from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

import certifi

ca = certifi.where()

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.pbhz9.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta
#
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('login.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>', methods=['GET'])
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})

        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        try:
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        except AttributeError:
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                   # 비밀번호
        "nickname": nickname_receive                                # 이름(닉네임)
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/check_dupnick', methods=['POST'])
def check_dupnick():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route("/main/<username>", methods=['GET'])
def main(username):
    user_info = db.users.find_one({"username": username}, {"_id": False})
    # username find_one nickname 받은 후 assign
    score_list = list(db.golf_scores.find({"username": username}, {'_id': False}))
    if len(score_list) != 0:
        total_score, count = 0, 0
        for record in score_list:
            total_score += int(record['score'])
            count += 1
        average_score = total_score / count
    else:
        average_score = 0
    return render_template("main.html", user_info=user_info, average_score=int(average_score))

@app.route("/golf", methods=["POST"])
def score_post():
    username_receive = request.form['username_give']
    date_receive = request.form['date_give']
    field_receive = request.form['field_give']
    score_receive = request.form['score_give']

    doc = {
        'username': username_receive,
        'date': date_receive,
        'field': field_receive,
        'score': score_receive
    }

    db.golf_scores.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})

@app.route("/golf", methods=["GET"])
def score_get():
    score_list = list(db.golf_scores.find({}, {'_id': False}))
    return jsonify({'golf_scores': score_list})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        nickname_receive = request.form["nickname_give"]
        password_receive = request.form["password_give"]
        area_receive = request.form["area_give"]
        tbox_receive = request.form["tbox_give"]
        address_receive = request.form["address_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_nickname": nickname_receive,
            "profile_password": password_receive,
            "profile_area": area_receive,
            "profile_address": address_receive,
            "profile_nickname": nickname_receive,
            "profile_tbox": tbox_receive,
            "profile_info": about_receive
        }

        db.users.update_one({'username': payload['id']}, {'$set':new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/mypage_in', methods=['POST'])
def mypage_in():
    nickname_receive = request.form['nickname_give']
    user_info = db.users.find_one({"nickname": nickname_receive}, {"_id": False})
    return jsonify({"result": "success", "user_info": user_info})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
