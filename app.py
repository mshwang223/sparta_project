from flask import Flask, render_template, request, jsonify, json
app = Flask(__name__)

from bson.objectid import ObjectId
from pymongo import MongoClient
# import certifi
# ca = certifi.where()

# client = MongoClient('mongodb+srv://test:sparta@cluster0.gmolb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=ca)
client = MongoClient('localhost', 27017)
db = client.dbsparta

## HTML 화면 보여주기
@app.route('/')
def login():
   return render_template('login.html')

@app.route('/main')
def main():
   return render_template('main.html')

@app.route('/contact')
def contact():
   return render_template('contact.html')

@app.route('/admin')
def admin():
   return render_template('admin.html')

@app.route('/diary')
def diary():
   return render_template('diary.html')

# 사용자 가입(POST) API
@app.route('/users', methods=['POST'])
def save_users():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nm_receive = request.form['nm_give']
    chk_author = request.form['au_give']

    # 수정 저장 여부
    chk_btn = request.form['chk_btn']

    # PK 대신 사용
    tmp_id = request.form['tmp_id']
    tmp_pw = request.form['tmp_pw']

    doc = {'id': id_receive,
           'pw': pw_receive,
           'name': nm_receive,
           'author': chk_author
          }

    # 동일한 id가 있는지 확인.
    target_user = db.users.find_one({'id': id_receive}, {'_id': False})

    # 수정인지 저장인지 구분
    if (int(chk_btn) == 0):
        # 동일한 id 여부 확인
        if (target_user):
            return jsonify({'msg': '동일한 ID를 가진 사용자가 있습니다.', 'result': 'error'})

        db.users.insert_one(doc)
        return jsonify({'msg': '가입이 완료되었습니다!', 'result': 'success'})
    else :
        # 동일한 id 여부 확인
        if (target_user):
            if (tmp_id != target_user['id']):
                return jsonify({'msg': '동일한 ID를 가진 사용자가 있습니다.', 'result': 'error'})
            # 변경 사항 여부 확인
            elif (id_receive == target_user['id'] and pw_receive == target_user['pw']
              and nm_receive == target_user['name'] and chk_author == target_user['author']):
                return jsonify({'msg': '변경할 내역이 없습니다.', 'result': 'error'})
        db.users.update_one({'id': tmp_id, 'pw': tmp_pw}, {'$set': doc})
        return jsonify({'msg': '수정 되었습니다!', 'result': 'success'})

# 사용자 삭제(POST) API
@app.route('/users/delete', methods=['POST'])
def delete_users():
    users_data = request.form['users_data']
    
    # JSON API 사용
    json_data = json.loads(users_data)

    for users in json_data:
        db.users.delete_one({'id':users['userid'], 'pw':users['userpw'], 'name':users['name']})

    return jsonify({'msg': '삭제되었습니다!'})

# 사용자 목록보기(GET) API
@app.route('/users', methods=['GET'])
def view_users():
    users_info = list(db.users.find({}, {'_id': False}))

    return jsonify({'users_info': users_info})

# 로그인 확인(GET, POST) API
@app.route('/login', methods=['GET', 'POST'])
def chk_users():
    id_receive = request.form['loginId_give']
    pw_receive = request.form['loginPw_give']

    users_info = list(db.users.find({}, {'_id': False}))
    for user in users_info:
        if (id_receive == user['id'] and pw_receive == user['pw']):
            return jsonify({'msg': '로그인 되었습니다!', 'user_info': user})
        pass

# 일기 저장(POST) API
@app.route('/diary/save', methods=['POST'])
def save_diary():
    date_receive = request.form['give_date']
    location_receive = request.form['give_location']
    angry_receive = request.form['give_angry']
    target_receive = request.form['give_target']
    reason_receive = request.form['give_reason']
    contents_receive = request.form['give_contents']

    # user_id 확인.
    id_receive = request.form['give_id']
    pw_receive = request.form['give_pw']

    target_user = db.users.find_one({'id': id_receive, 'pw': pw_receive}, {'_id': True})

    doc = {'date': date_receive,
           'location': location_receive,
           'angry': angry_receive,
           'target': target_receive,
           'reason': reason_receive,
           'contents': contents_receive,
           'userid': str(target_user['_id'])
          }

    db.diary.insert_one(doc)

    return jsonify({'msg': '일기가 저장되었습니다!'})

# 일기 목록보기(GET) API
@app.route('/diary/lists', methods=['GET'])
def view_diary():
    diary_info = list(db.diary.find({}, {'_id': False}).sort('date'))
    diary_date = list(db.diary.aggregate([{'$group' : {'_id':'$date'}}, {'$sort': {'_id' : 1}}]))
    users = []

    # 이름가져오기
    for user in diary_info:
        target_user = db.users.find_one({'_id': ObjectId(user['userid'])})
        user['name'] = str(target_user['name'])
        users.append(user)

    return jsonify({'diary_info': users, 'diary_date': diary_date})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)