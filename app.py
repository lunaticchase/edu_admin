from flask import Flask, jsonify, sessions, request, make_response
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
import json
import os
import hashlib
from config import *
import pymysql

app = Flask(__name__)
# CORS(app, supports_credentials=True)
app.config.from_object(__name__)
app.config["SECRET_KEY"] = os.urandom(24)


@app.after_request
def af_request(resp):
    """
     #请求钩子，在所有的请求发生后执行，加入headers。
    :param resp:
    :return:
    """
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp


@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        return jsonify({"code": "1"})
    else:
        return jsonify({"code": "2", "message": "请求方式不正确"})


@app.route("/login", methods=["POST"])
def login():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data, encoding="utf-8")
        mailbox = data["mailbox"] if "mailbox" in data else ""
        password = data["password"] if "password" in data else ""
        if not (mailbox or password):
            return jsonify({"code": "2", "message": "账号密码不能为空"})
        psword = hashlib.md5()
        psword.update(password.encode(encoding="utf-8"))
        password = psword.hexdigest()
        password = password[:10]
        db = SQLManager()
        messages = db.get_one("select * from edu_message where mailbox='%s'" % mailbox)
        teache = db.get_one("select * from techer_meaage where tearch_mailbox='%s'" % mailbox)
        if messages:
            if password == messages["password"]:
                print(messages["name"])
                return jsonify({"code": "1"})
            else:
                return jsonify({"code": "2", "message": "账号密码不正确"})
        elif teache:
            if password == teache["tearch_password"]:
                # sessions["username"] = messages["name"]
                return jsonify({"code": "1"})
            else:
                return jsonify({"code": "2", "message": "账号密码不正确"})
        else:
            return jsonify({"code": "2", "message": "信息不存在"})
    else:
        return jsonify({"code": "2", "message": "请求方式不对"})


@app.route("/information", methods=["POST"])
def information():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data, encoding="utf-8")
        mailbox = data["mailbox"] if "mailbox" in data else ""
        db = SQLManager()
        messages = db.get_one("select * from edu_message where mailbox='%s'" % mailbox)
        teache = db.get_one("select * from techer_meaage where tearch_mailbox='%s'" % mailbox)
        if messages:
            name = messages["name"] if "name" in messages else ""
            age = messages["age"] if "age" in messages else ""
            sex = messages["sex"] if "sex" in messages else ""
            diction = messages["diction"] if "diction" in messages else ""
            id = messages["stu_id"] if "stu_id" in messages else ""
            return jsonify({"code": "1", "name": name, "age": age, "sex": sex, "diction": diction, "id": id,
                            "curriculum_id": messages["curriculum_id"]})
        elif teache:
            name = teache["tearch_name"] if "tearch_name" in teache else ""
            age = teache["tearch_age"] if "tearch_age" in teache else ""
            sex = teache["tearch_sex"] if "tearch_sex" in teache else ""
            diction = teache["diction"] if "diction" in teache else ""
            id = teache["techer_id"] if "techer_id" in teache else ""
            return jsonify({"code": "1", "name": name, "age": age, "sex": sex, "diction": diction, "id": id})
        else:
            return jsonify({"code": "2", "message": "此用户信息有误"})
    else:
        return jsonify({"code": "2", "message": "请求方式不正确"})


@app.route("/curriculum", methods=["POST"])
def curriculum():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data, encoding="utf-8")
        diction = data["diction"] if "diction" in data else ""
        id = data["id"] if "id" in data else ""
        if diction:
            if not id:
                return jsonify({"code": "2", "message": "学生序号不正确"})
            db = SQLManager()
            messages = db.get_one("select * from edu_message where stu_id='%s'" % id)
            curriculum_id = messages["curriculum_id"] if "curriculum_id" in messages else ""
            curriculum_list = curriculum_id.strip(",").split(",")
            curr_list = list()
            for curriculum_id in curriculum_list:
                curriculum_dict = dict()
                # print(curriculum_id)
                curriculum_message = db.get_list(
                    "select * from curriculum where curriculum_id='%s'" % curriculum_id)
                for curriculum_info in curriculum_message:
                    curriculum_name = curriculum_info[
                        "curriculum_nacurriculum_name"] if "curriculum_nacurriculum_name" in curriculum_info else ""
                    curriculum_num = curriculum_info[
                        "curriculum_num"] if "curriculum_num" in curriculum_info else ""
                    curriculum_id = curriculum_info["curriculum_id"] if "curriculum_id" in curriculum_info else ""
                    if diction == "1":
                        techer_id = curriculum_info["techer_id"] if "techer_id" in curriculum_info else ""
                        techer_message = db.get_one("select * from techer_meaage where techer_id='%s'" % techer_id)
                        te_name = techer_message["tearch_name"] if "tearch_name" in techer_message else ""
                        sql = "select score_num as s_num from score as s inner join edu_message as edu on (edu.score_id = s.score_id) inner join  curriculum as cur on(cur.score_id = s.score_id)"
                        score_num = db.get_one(sql)
                        score_num = score_num["s_num"]
                        curriculum_dict["curriculum_name"] = curriculum_name
                        curriculum_dict["curriculum_num"] = curriculum_num
                        curriculum_dict["curriculum_id"] = curriculum_id
                        curriculum_dict["score"] = score_num
                       	curriculum_dict["teache_name"] = te_name
                        curr_list.append(curriculum_dict)
                    elif diction == "2" or "3":
                        curriculum_dict["curriculum_name"] = curriculum_name
                        curriculum_dict["curriculum_num"] = curriculum_num
                        curriculum_dict["curriculum_id"] = curriculum_id
                        curr_list.append(curriculum_dict)
        else:
            return jsonify({"code": "2", "message": "权限不正确"})
        return jsonify({"code": "1", "curriculum_message": curr_list})


@app.route("/see_student", methods=["POST"])
def see_student():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data, encoding="utf-8")
        diction = data["diction"] if "diction" in data else ""
        if diction == "2":
            curriculum_id = data["curriculum_id"] if "diction" in data else ""
            db = SQLManager()
            curriculum_messages = db.get_one("select * from curriculum where curriculum_id='%s'" % curriculum_id)
            stu_list = curriculum_messages["stu_id"] if "stu_id" in curriculum_messages else ""
            stu_list = stu_list.strip(",").split(",")
            stu_message = list()

            for stu_id in stu_list:
                stu_dt = dict()
                stu_name = db.get_list("select name from edu_message where  stu_id = '%s'" % stu_id)
                for name in stu_name:
                    stu_dt["stu_id"] = stu_id
                    stu_dt["sut_name"] = name["name"]
                stu_message.append(stu_dt)
        else:
            return jsonify({"code": "2", "message": "权限不够"})
        return jsonify({"code": "1", "stu_meaages": stu_message})


@app.route("/point_student", methods=["POST"])
def point_student():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data, encoding="utf-8")
        sut_id = data["sut_id"] if "sut_id" in data else ""
        curriculum_id = data["curriculum_id"] if "curriculum_id" in data else ""
        score_num = data["score_num"] if "score_num" in data else ""
        print(score_num)
        db = SQLManager()
        score_msg = db.get_list("select * from score  where (stu_id = '%s' and curriculum_id = '%s')" % (sut_id,curriculum_id))
        if score_msg:
            return jsonify({"code": "2", "message": "已经打过分数请不要重复打分"})
        try:
            cur = db.create("insert into score(stu_id,curriculum_id,score_num) value('%s','%s',%d)" %(sut_id, curriculum_id, int(score_num)))
        except Exception as e:
            return jsonify({"code": "2", "message": "%s" % e})
        return jsonify({"code": "1"})


@app.route("/found_work", methods=["POST"])
def found_word():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data, encoding="utf-8")
        found_message = data["found_message"] if "found_message" in data else ""
        curriculum_id = data["curriculum_id"] if "curriculum_id" in data else ""
        db = SQLManager()
        try:
            cur = db.create("insert into curriculum(stu_id,curriculum_id,score_num) value('%s','%s',%d)" % ())
        except Exception as e:
            return jsonify({"code": "2", "message": "%s" % e})
        return jsonify({"code": "1"})

# @app.route('/index')
# def hello_world():
#   return 'Hello World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=500,debug=True)

