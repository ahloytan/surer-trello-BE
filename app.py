from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from flask_restx.swagger import build_request_body_parameters_schema
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import hashlib, uuid
import traceback
import secrets
from datetime import datetime, timedelta
import json
import requests
from utils import default
import os
import ast

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Surer(FE)",
    description="Aloysius Tan",
)

CORS(app, supports_credentials=True)
load_dotenv()

# ==================== CONNECTING TO DATABASE ====================#
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_endpoint = os.getenv("DB_ENDPOINT")
BASE_URL = os.getenv("BASE_URL")
app.config["CORS_HEADERS"] = "Content-Type"
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_endpoint}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["CORS_ALLOW_CREDENTIALS"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
db = SQLAlchemy(app)

################## User Class Creation ##################
class User(db.Model):
    __tablename__ = "user"

    email = db.Column(db.String(256), primary_key=True)
    hashed_password = db.Column(db.String(256),nullable=True)
    salt = db.Column(db.String(256),nullable=True)
    first_name = db.Column(db.String(256),nullable=False)
    last_name = db.Column(db.String(256),nullable=False)

    def __init__(self, email, hashed_password, salt, first_name, last_name):
        self.email = email
        self.hashed_password = hashed_password
        self.salt = salt
        self.first_name = first_name
        self.last_name = last_name

    def json(self):
        return {"email": self.email, "hashed_password": self.hashed_password, "salt":self.salt,"first_name":self.first_name, "last_name": self.last_name}

################## Project Class Creation ##################
class Project(db.Model):
    __tablename__ = "project"

    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    last_modified = db.Column(db.DateTime, nullable=False)

    def __init__(self, creator, description, created_at, last_modified):
        self.creator = creator
        self.description = description
        self.created_at = created_at
        self.last_modified = last_modified

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

################## Team Class Creation ##################
class Team(db.Model):
    __tablename__ = "team"

    user_email = db.Column(db.String(256), db.ForeignKey('user.email'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), primary_key=True)

    def __init__(self, user_email, project_id):
        self.user_email = user_email
        self.project_id = project_id

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

################## Task Class Creation ##################
class Task(db.Model):
    __tablename__ = "task"

    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False)
    title = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_datetime = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    completion_status = db.Column(db.String(256), nullable=True)

    def __init__(self, project_id, title,description, position, created_datetime, deadline, completion_status):
        self.project_id = project_id
        self.title = title
        self.description = description
        self.position = position
        self.created_datetime = created_datetime
        self.deadline = deadline
        self.completion_status = completion_status

    def json(self):
        return {"task_id": self.task_id, "project_id": self.project_id, "title":self.title, "description": self.description, "position": self.position, "created_datetime":self.created_datetime, "deadline":self.deadline, "completion_status": self.completion_status}

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

################## Assignee Class Creation ##################
class Assignee(db.Model):
    __tablename__ = "assignee"

    task_id = db.Column(db.Integer, db.ForeignKey('task.task_id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), primary_key=True)
    user_email = db.Column(db.String(256), db.ForeignKey('user.email'),primary_key=True)
    fname = db.Column(db.String(256), nullable=False)
    lname = db.Column(db.String(256), nullable=False)


    def __init__(self, task_id, project_id, user_email, fname, lname):
        self.task_id = task_id
        self.project_id = project_id
        self.user_email = user_email
        self.fname = fname
        self.lname = lname

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

################## Sessions Class Creation ##################
class Sessions(db.Model):
    __tablename__ = "sessions"

    user_email = db.Column(db.String(256), db.ForeignKey('user.email'), primary_key=True)
    session_id = db.Column(db.String(256), primary_key=True)

    def __init__(self, user_email, session_id):
        self.user_email = user_email
        self.session_id = session_id

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
# ==================== CONNECTED TO DATABASE ====================#


test_parser = api.parser()
test_parser.add_argument("number1", help="First number to add")
test_parser.add_argument("number2", help="Second number to add")
@api.route("/test", methods=["GET","POST"])
@api.doc(
    description="Adds 2 numbers. Just testing the endpoint."
)
class Test(Resource):
    @api.expect(test_parser)
    def get(self):
        number1 = test_parser.parse_args().get("number1")
        number2 = test_parser.parse_args().get("number2")
        try:
            return (int(number1) + int(number2)), 200
        except:
            return "Error", 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
