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
    details = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    last_modified = db.Column(db.DateTime, nullable=False)

    def __init__(self, creator, description, created_at, last_modified):
        self.creator = creator
        self.description = description
        self.details = details
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

# ==================== USER FUNCTIONS ====================#

# user_registration_parser = api.parser()
# user_registration_parser.add_argument("email", help="Unique email used to register")
# user_registration_parser.add_argument("password", help="Corresponding password")
# user_registration_parser.add_argument("first_name", help="First name of user")
# user_registration_parser.add_argument("last_name", help="Last name of user")
user_registration_parser = api.model("user_model",{
    'email': fields.String(description="Email of user", required=True),
    'password': fields.String(description="Password of user", required=True),
    'first_name': fields.String(description="User's first name", required=True),
    'last_name': fields.String(description="User's last name", required=True),
})
@api.route("/user_registration")
@api.doc(description="User registration")
class UserRegistration(Resource):
    @api.expect(user_registration_parser)
    def post(self):
        data = request.get_json()
        data = json.loads(json.dumps(data))
        email = data["email"]
        password = data["password"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        acc = User.query.filter_by(email=email).count()

        if acc > 0:
            exists=True
        else:
            exists=False
        if exists:
            return json.loads(json.dumps({
                "error": "Email already exist"
            }, default=default)), 422
        else:
            salt = uuid.uuid4().hex
            hashed_password= hashlib.sha512((password + salt).encode('utf-8')).hexdigest()
            user = User(email,hashed_password, salt, first_name, last_name)
        try:
            session_id = secrets.token_urlsafe(16)
            user_session = Sessions(email, session_id)
            db.session.add(user)
            db.session.commit()
            db.session.add(user_session)
            db.session.commit()
            return json.loads(json.dumps({
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }, default=default)), 200, { 'Set-Cookie':f'SESSION_ID={session_id}; Path=/; HttpOnly; SameSite=None; Secure' }
        except Exception as e:
            print(e)
            return json.loads(json.dumps({
                "error": "Unexpected error in registration. Please try again."
            }, default=default)), 500



user_login_parser = api.model("user_login_model",{
    'email': fields.String(description="Email of user", required=True),
    'password': fields.String(description="Password of user", required=False),
    'first_name': fields.String(description="First name of user for first time google log in", required=False),
    'last_name': fields.String(description="Last of user for first time google log in", required=False),
})
@api.route("/user_login")
@api.doc(description="User login")
class UserLogin(Resource):
    @api.expect(user_login_parser)
    def post(self):
        data = request.get_json()
        data = json.loads(json.dumps(data))
        email = data["email"]

        try:
            user = User.query.get(email)
            if user:
                user = user.json()
                if user["hashed_password"]:
                    # Check if google log in. If fname and lname exists, user already has an account
                    if "first_name" in data and "last_name" in data:
                        return json.loads(json.dumps({
                            "error": f"You already have an account. Log in with {user['email']}"
                        }, default=default)), 401
                    # Normal log in, validate pw
                    password = data["password"]
                    hashed_db_password = user["hashed_password"]
                    db_salt = user["salt"]
                    hashed_password = hashlib.sha512((password + db_salt).encode('utf-8')).hexdigest()
                    if hashed_password != hashed_db_password:
                        return json.loads(json.dumps({"error": "Incorrect password"}, default=default)), 422
                else:
                    if "first_name" not in data and "last_name" not in data:
                        return json.loads(json.dumps({
                            "error": "You already have an account. Log in with Google account!"
                        }, default=default)), 422


                # Google login and if normal log in pw verified
                session_id = secrets.token_urlsafe(16)
                current_session = Sessions.query.filter_by(user_email=email).first()

                if current_session:
                    current_session.session_id = session_id
                else:
                    user_session = Sessions(email, session_id)
                    db.session.add(user_session)
                db.session.commit()
                print("google log in")
                return json.loads(json.dumps({
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                }, default=default)), 200, { 'Set-Cookie':f'SESSION_ID={session_id}; Path=/; HttpOnly; SameSite=None; Secure' }
            else:
                # Check if google log in. If fname and lname does not exist, log in type is normal
                if "first_name" not in data and "last_name" not in data:
                    return json.loads(json.dumps({"error": "User does not exist"}, default=default)), 422
                else:
                    # First time google log in, register user
                    first_name = data["first_name"]
                    last_name = data["last_name"]
                    new_user = User(email, None, None, first_name, last_name)
                    db.session.add(new_user)
                    db.session.commit()

                    session_id = secrets.token_urlsafe(16)
                    user_session = Sessions(email, session_id)
                    db.session.add(user_session)
                    db.session.commit()

                    return json.loads(json.dumps({
                        "email": data["email"],
                        "first_name": data["first_name"],
                        "last_name": data["last_name"],
                    }, default=default)), 200, { 'Set-Cookie':f'SESSION_ID={session_id}; Path=/; HttpOnly; SameSite=None; Secure' }

        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Something went wrong with logging in"}, default=default)), 500

@api.route("/user_logout")
@api.doc(description="User logout")
class UserLogout(Resource):
    def post(self):
        session_id = request.cookies.get('SESSION_ID')

        try:
            Sessions.query.filter_by(session_id=session_id).delete()
            db.session.commit()
            return json.loads(json.dumps({"message": "success"}, default=default)), 200
        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Something went wrong with logging out"}, default=default)), 500

# ==================== TEAM FUNCTIONS ====================#

#Join Team
join_team_model = api.model("join_team_model",{
    'email': fields.String(description="Email of user", required=True),
    'team_id': fields.Integer(description="team ID to join (same as project id)", required=True),
})
@api.route("/join_team")
@api.doc(description="Join Team")
class JoinTeam(Resource):
    @api.expect(join_team_model)
    def post(self):
        data = request.get_json()
        email = data["email"]
        team_id = data["team_id"]
        try:
            join_team = Team(email,team_id)
            db.session.add(join_team)
            db.session.commit()

            project = Project.query.get(team_id)
            if project:
                project = project.as_dict()
                team = Team.query.filter_by(project_id=team_id)
                project_members = []
                for member in team:
                    member = member.as_dict()
                    member_info = User.query.get(member["user_email"])
                    member = {
                        "user_email": member_info.email,
                        "fname": member_info.first_name,
                        "lname": member_info.last_name,
                    }
                    project_members.append(member)

                project["members"] = project_members
            return json.loads(json.dumps(project, default=str)), 200
        except Exception as e:
            print(e)
            return "Error, please try again", 400

#Get user teams
get_user_teams_parser = api.parser()
get_user_teams_parser.add_argument("email", help="Email of user to retrieve teams for")
@api.route("/get_user_teams")
@api.doc(description="Get teams that a user belongs to")
class GetUserTeams(Resource):
    @api.expect(get_user_teams_parser)
    def get(self):
        email = get_user_teams_parser.parse_args().get("email")
        projects_list = [] #returns list of project ids that a user is in
        for team in Team.query.filter_by(user_email=email):
            project = Project.query.get(team.project_id)
            project_info = {}
            project_info["project_id"] = team.project_id
            project_info["creator"] = project.as_dict()["creator"]
            project_info["description"] = project.as_dict()["description"]
            project_info["created_at"] = project.as_dict()["created_at"].strftime("%Y-%m-%d")
            project_info["last_modified"] = project.as_dict()["last_modified"].strftime("%Y-%m-%d")
            project_id = team.project_id
            project_team = Team.query.filter(Team.project_id==project_id)
            project_members = []
            for member in project_team:
                member = member.as_dict()
                member_info = User.query.get(member["user_email"])
                member = {
                    "user_email": member_info.email,
                    "fname": member_info.first_name,
                    "lname": member_info.last_name,
                }
                project_members.append(member)
            project_info['members'] = project_members
            projects_list.append(project_info)
            # projects_list.append(team.project_id)
        return projects_list, 200

# ==================== PROJECT FUNCTIONS ====================#
# create_project_parser = api.parser()
# create_project_parser.add_argument("email", help="Email of creator of project team")
# create_project_parser.add_argument("description", help="Description of project")
# user_fields = api.model('UserInfo', {
#     'fname': fields.String,
#     'lname': fields.String,
#     "email": fields.String
# })
create_project_model = api.model("create_project_model",{
    'creator': fields.String(description="Email of creator", required=True),
    'description': fields.String(description="Any description of project", required=True)
})

@api.route("/create_project")
@api.doc(description="Create Project")
class CreateProject(Resource):
    @api.expect(create_project_model)
    def post(self):
        new_project = api.payload
        data = request.get_json()
        data=json.loads(json.dumps(data))
        creator = data["creator"]
        description = data["description"]
        created_at = str(datetime.today())
        created_at_object = datetime(int(created_at.split("-")[0]), int(created_at.split("-")[1]), int(created_at.split("-")[2].split(" ")[0]))
        last_modified_object = datetime(int(created_at.split("-")[0]), int(created_at.split("-")[1]), int(created_at.split("-")[2].split(" ")[0]))

        new_project = Project(creator,description,created_at_object,last_modified_object)
        try:
            db.session.add(new_project)
            db.session.commit()
            new_project_id = new_project.project_id
            new_team = Team(creator, new_project_id)
            db.session.add(new_team)
            db.session.commit()

            user = request.user
            member_info = User.query.get(user)
            member = {
                "user_email": member_info.email,
                "fname": member_info.first_name,
                "lname": member_info.last_name,
            }

            project = Project.query.get(new_project.project_id)
            if project:
                project = project.as_dict()
                project['members'] = [member]

            return json.loads(json.dumps(project, default=str)), 200
        except Exception as e:
            print(e)
            return "Failed", 400

get_project_parser = api.parser()
get_project_parser.add_argument("email", help="Unique email of user")
@api.route("/get_project")
@api.doc(description="Get list of projects by user (email id)")
class GetProject(Resource):
    @api.expect(get_project_parser)
    def get(self):
        email = get_project_parser.parse_args().get("email")
        print(email)
        project_info = {}
        for proj in Project.query.filter_by(creator=email):
            project_info[proj.project_id] = {}
            project_info[proj.project_id]["email"] = proj.as_dict()["creator"]
            project_info[proj.project_id]["description"] = proj.as_dict()["description"]
            created_at = proj.as_dict()["created_at"].strftime("%Y-%m-%d")
            project_info[proj.project_id]["created_at"] = created_at
            last_modified = proj.as_dict()["last_modified"].strftime("%Y-%m-%d")
            project_info[proj.project_id]["last_modified"] = last_modified
        if project_info == {}:
            return "No projects", 400
        return project_info, 200

get_project_parser = api.parser()
@api.route("/get_all_project_ids")
@api.doc(description="Getall project ids")
class GetProject(Resource):
    @api.expect(get_project_parser)
    def get(self):
        project_info = []
        for proj in Project.query.filter_by():
            project_info.append(proj.project_id)
        if project_info == []:
            return "No projects", 400
        return project_info, 200

get_project_id_parser = api.parser()
get_project_id_parser.add_argument("project_id", help="Unique project id")
@api.route("/project")
class GetProjectByID(Resource):
    @api.expect(get_project_id_parser)
    def get(self):
        project_id = get_project_id_parser.parse_args().get("project_id")
        user = request.user
        try:
            user_projects = Team.query.get((user, project_id))
            if user_projects is None:
                return json.loads(json.dumps({"error": "Unauthorized request"}, default=default)), 403

            project = Project.query.get(project_id)
            if project:
                project = project.as_dict()
                team = Team.query.filter(Team.project_id==project_id)
                project_members = []
                for member in team:
                    member = member.as_dict()
                    member_info = User.query.get(member["user_email"])
                    member = {
                        "user_email": member_info.email,
                        "fname": member_info.first_name,
                        "lname": member_info.last_name,
                    }
                    project_members.append(member)

                project["members"] = project_members
                return json.loads(json.dumps(project, default=str)), 200
            else:
                return json.loads(json.dumps({
                    "error": "Project id does not exist"
                }, default=str)), 400
        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Unable to retrieve project"}, default=default)), 500


change_proj_details_parser = api.parser()
change_proj_details_parser.add_argument("project_id", help="Reference project id")
change_proj_details_parser.add_argument("description", help="Change code name")
change_proj_details_parser.add_argument("details", help="Change details")
@api.route("/change_proj_details")
@api.doc(description="Change Project Details")
class ChangeProjectDetails(Resource):
    @api.expect(change_proj_details_parser)
    def get(self):
        proj_id = change_proj_details_parser.parse_args().get("project_id")
        description = change_proj_details_parser.parse_args().get("description")
        details = change_proj_details_parser.parse_args().get("details")
        try:
            proj = Project.query.get((proj_id))
            print(proj.description, proj.details)
            print(description, details)
            proj.description = description
            proj.details= details
            db.session.commit()

            return json.loads(json.dumps({'name' : proj.description, 'desc' : proj.details}, default=str)), 200
        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Unable to retrieve project details"}, default=default)), 500

# ==================== TASK FUNCTIONS ====================#
# ----- Create Task ----- #
# create_task_parser = api.parser()
# create_task_parser.add_argument("project_id", help="Project ID")
# create_task_parser.add_argument("description", help="Description of task")
# create_task_parser.add_argument("position", type= int, help="Position of task")
# create_task_parser.add_argument("deadline", help="deadline for task")
# create_task_parser.add_argument("completion_status", help="Task's completion status (not started/started/completed)")
user_fields = api.model('UserInfo', {
    'fname': fields.String,
    'lname': fields.String,
    "user_email": fields.String
})
create_task_model = api.model("create_task_model",{
    'task_id': fields.Integer(description="Task ID", required=True),
    'project_id': fields.Integer(description="Project ID", required=True),
    'title': fields.String(description="Title of task", required=True),
    'description': fields.String(description="Description of task"),
    'position': fields.Integer(description="Position of task", required=True),
    'deadline': fields.DateTime(description="Deadline of task"),
    'completion_status': fields.String(description="Status of task", required=True),
    'assignees': fields.List(fields.Nested(user_fields)),
})

@api.route("/create_task")
@api.doc(description="Create Task")
class CreateTask(Resource):
    @api.expect(create_task_model)
    def post(self):
        data = request.get_json()
        data = json.loads(json.dumps(data))
        project_id = data["project_id"]
        title = data["title"]
        description = data["description"]
        position = data["position"]
        created_datetime = datetime.now(tz=None)
        deadline = data["deadline"]
        print(deadline)
        print(type(deadline))
        if deadline is not None:
            deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
            deadline = deadline + timedelta(hours=8)
        if description is None:
            description = "<No description entered>"
        completion_status = data["completion_status"]
        assignees = data["assignees"]
        new_task = Task(project_id, title,description, position, created_datetime, deadline, completion_status)
        try:
            db.session.add(new_task)
            db.session.commit()

            for assignee in assignees:
                new_assignees = Assignee(new_task.task_id, project_id, assignee["user_email"], assignee["fname"], assignee["lname"])
                db.session.add(new_assignees)
            db.session.commit()
            response = {
                **new_task.as_dict(),
                "assignees": assignees,
            }
            return json.loads(json.dumps(response, default=str)), 200

        except Exception as e:
            print(e)
            error_str = traceback.format_exc()
            return json.loads(json.dumps({"error": "Unable to create task"}, default=default)), 500

# ----- Get Task By Project ID ----- #
get_task_by_project_parser = api.parser()
get_task_by_project_parser.add_argument("project_id", help="Enter project ID")
@api.route("/get_task_by_projectid")
@api.doc(description="Get list of tasks by project (project id)")
class GetTaskByProject(Resource):
    @api.expect(get_task_by_project_parser)
    def get(self):
        project_id = get_task_by_project_parser.parse_args().get("project_id")
        user = request.user
        todo = []
        inprogress = []
        completed = []
        try:
            user_projects = Team.query.get((user, project_id))
            if user_projects is None:
                return json.loads(json.dumps({"error": "Unauthorized request"}, default=default)), 403

            tasks = Task.query.order_by(Task.position.asc()).filter_by(project_id=project_id).all()
            for task in tasks:
                task = task.as_dict()
                assignees = Assignee.query.filter_by(task_id=task["task_id"]).all()
                all_assignees = []
                for assignee in assignees:
                    assignee = assignee.as_dict()
                    del assignee["project_id"]
                    del assignee["task_id"]
                    all_assignees.append(assignee)
                task["assignees"] = all_assignees

                if task["completion_status"] == "not started":
                    todo.append(task)
                elif task["completion_status"] == "started":
                    inprogress.append(task)
                elif task["completion_status"] == "completed":
                    completed.append(task)
                else:
                    raise Exception("Invalid completion_status")
            return json.loads(json.dumps({
                "tasks": {
                    "todo": todo,
                    "inprogress": inprogress,
                    "completed": completed,
                }
            }, default=str)), 200
        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Unable to retrieve tasks"}, default=default)), 500

task_model = api.model("task_model", {
    'project_id': fields.Integer(description="Project ID", required=True),
    'task_id': fields.Integer(description="Task ID", required=True),
    'title': fields.String(description="Title of task", required=True),
    'description': fields.String(description="Description of task"),
    'position': fields.Integer(description="Position of task", required=True),
    'deadline': fields.DateTime(description="Deadline of task"),
    'completion_status': fields.String(description="Status of task", required=True),
    'assignees': fields.List(fields.Nested(user_fields)),
})


# ----- Update Task ----- #
@api.route("/update_task")
@api.doc(description="Update task)")
class UpdateTask(Resource):
    @api.expect(create_task_model)
    def patch(self):
        data = request.get_json()
        data = json.loads(json.dumps(data))
        task_id = data["task_id"]

        try:
            task = Task.query.get(task_id)
            original_deadline = task.deadline
            new_deadline = data["deadline"]
            new_deadline_string = new_deadline.split("T")[0].strip()
            new_deadline = datetime.strptime(new_deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
            new_deadline = new_deadline + timedelta(hours=8)
            original_deadline = str(original_deadline).split(" ")[0]
            original_deadline_string = original_deadline
            if task:
                task.description = data["description"]
                task.title = data["title"]
                task.deadline = new_deadline
                updated_assignees = data["assignees"]
                current_assignees = Assignee.query.filter_by(task_id=task_id).all()
                current_assignees = [assignee.as_dict()["user_email"] for assignee in current_assignees]
                # add new assignees
                for assignee in updated_assignees:
                    if assignee["user_email"] not in current_assignees:
                        new_assignee = Assignee(task_id, data["project_id"], assignee["user_email"], assignee["fname"], assignee["lname"])
                        db.session.add(new_assignee)
                # delete assignees who are unassigned
                updated_assignees = [assignee["user_email"] for assignee in updated_assignees]
                print(updated_assignees)
                for current_assignee in current_assignees:
                    if current_assignee not in updated_assignees:
                        Assignee.query.filter_by(task_id=task_id).filter_by(user_email=current_assignee).delete()
                db.session.commit()
                new_deadline = str(original_deadline).split(" ")[0]
                if original_deadline != new_deadline_string:
                    for new_assignee_email in updated_assignees:
                        data = {
                        'Messages': [
                                {
                                "From": {
                                    "Email": "taskucci@gmail.com",
                                    "Name": "Taskucci"
                                },
                                "To": [
                                    {
                                    "Email": f"{new_assignee_email}",
                                    "Name": f"{new_assignee_email}"
                                    }
                                ],
                                "Subject": f"{task.title}: Task Deadline Updated",
                                "TextPart": "Thank you for using Taskucci project management board - where efficiency meets usability",
                                "HTMLPart": f"Dear {new_assignee_email},<br><br> Please check your Taskucci application to view updated task deadline for {task.title}. Thank you!",
                                "CustomID": "Task deadline updated"
                                }
                            ]
                        }
                return json.loads(json.dumps({"message":"success"}, default=default)), 200
            else:
                return json.loads(json.dumps({"error": f"Task {task_id} does not exist"}, default=default)), 400
        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Unable to update tasks"}, default=default)), 500

# ----- Update Task Position ----- #
task_position_model = api.model("task_position_model", {
    'project_id': fields.Integer(description="Project ID", required=True),
    'task_id': fields.Integer(description="Task ID", required=True),
    'new_position': fields.Integer(description="New position of task", required=True),
    # 'old_position': fields.Integer(description="Old position of task", required=True),
    'new_status': fields.String(description="Status of task", required=True),
})

@api.route("/update_task_position")
@api.doc(description="Update task position)")
class UpdateTaskPosition(Resource):
    @api.expect(task_position_model)
    def patch(self):
        data = request.get_json()
        data = json.loads(json.dumps(data))
        task_id = data["task_id"]
        project_id = data["project_id"]
        new_position = data["new_position"]
        new_status = data["new_status"]

        try:
            task = Task.query.get(task_id)

            old_position = task.position
            if task.completion_status == new_status:
                selected_tasks = Task.query.order_by(Task.position.asc()).filter_by(project_id=project_id).filter_by(completion_status=new_status).all()

                if old_position > new_position:
                    for i in range(new_position, old_position):
                        current_task = Task.query.get(selected_tasks[i].task_id)
                        selected_tasks[i].position = selected_tasks[i].position + 1
                else:
                    for i in range(old_position+1, new_position+1):
                        selected_tasks[i].position = selected_tasks[i].position - 1

                task.position = new_position
            else:
                # get tasks with old status
                old_status = task.completion_status
                old_status_tasks = Task.query.order_by(Task.position.asc()).filter_by(project_id=project_id).filter_by(completion_status=old_status).all()
                for i in range(old_position+1, len(old_status_tasks)):
                    old_status_tasks[i].position = old_status_tasks[i].position - 1

                # get tasks with new status
                new_status_tasks = Task.query.order_by(Task.position.asc()).filter_by(project_id=project_id).filter_by(completion_status=new_status).all()
                for i in range(new_position, len(new_status_tasks)):
                    new_status_tasks[i].position = new_status_tasks[i].position + 1

                # change status of task to new status
                task.position = new_position
                task.completion_status = new_status
            db.session.commit()
            return json.loads(json.dumps({"message": "success"}, default=default)), 200

        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Unable to update tasks"}, default=default)), 500

# ----- Delete Task  ----- #
delete_task_parser = api.parser()
delete_task_parser.add_argument("task_id", help="Enter task ID")
@api.route("/delete_task")
@api.doc(description="Delete task")
class DeleteTask(Resource):
    @api.expect(delete_task_parser)
    def delete(self):
        task_id = delete_task_parser.parse_args().get("task_id")

        try:
            task = Task.query.get(task_id)
            task_position = task.position
            status = task.completion_status
            project_id = task.project_id

            tasks = Task.query.order_by(Task.position.asc()).filter_by(project_id=project_id).filter_by(completion_status=status).all()
            for i in range(task_position+1, len(tasks)):
                tasks[i].position = tasks[i].position - 1
            Assignee.query.filter_by(task_id=task_id).delete()
            Task.query.filter_by(task_id=task_id).delete()

            db.session.commit()
            return json.loads(json.dumps({"message":"success"}, default=default)), 200
        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error":"Unable to delete task"}, default=default)), 500

# ----- START DASHBOARD ----- #
@api.route("/dashboard", methods=["GET"])
class Dashboard(Resource):
    def get(self):
        # Overall projects & per project
        #     4 boxes
        #         Total number of completed tasks
        #         Total number of incomplete tasks (todo, in progress)
        #         Number of overdue tasks -
        #         Total tasks -
        #     Bar graph
        #         Number of upcoming tasks by project (Todo)
        #         Number of tasks incomplete by project (todo, in progress)
        #     Pie chart
        #         Number of tasks by completion status (todo, in progress, completed)
        #     Line graph
        #         Number of due tasks this week

        user = request.user
        try:
            user_tasks = Assignee.query.filter_by(user_email=user)
            total_tasks = user_tasks.count()

            overall = {
                "no_completed_tasks": 0,
                "no_incomplete_tasks": 0,
                "no_overdue_tasks": 0,
                "total_tasks": total_tasks,
                "tasks_completion_status": {
                    "todo": 0,
                    "in_progress": 0,
                    "completed": 0
                },
                "no_due_this_week": [0,0,0,0,0,0,0]
            }

            stats_by_project = {}
            user_teams = Team.query.filter_by(user_email=user)

            for team in user_teams.all():
                project = Project.query.get(team.project_id)
                stats_by_project[project.project_id] = {
                    "description": project.description,
                    "no_completed_tasks": 0,
                    "no_incomplete_tasks": 0,
                    "no_overdue_tasks": 0,
                    "total_tasks": 0,
                    "no_upcoming_tasks": 0,
                    "tasks_completion_status": {
                        "todo": 0,
                        "in_progress": 0,
                        "completed": 0
                    },
                    "no_due_this_week": [0,0,0,0,0,0,0]
                }

            for task in user_tasks.all():
                task_info = Task.query.get(task.task_id)
                project_id = task_info.project_id
                stats_by_project[project_id]["total_tasks"] += 1

                if task_info.completion_status == 'completed':
                    overall["no_completed_tasks"] += 1
                    overall["tasks_completion_status"]["completed"] += 1
                    # by project
                    stats_by_project[project_id]["no_completed_tasks"] += 1
                    stats_by_project[project_id]["tasks_completion_status"]["completed"] += 1
                else:
                    overall["no_incomplete_tasks"] += 1

                    if task_info.completion_status == "started":
                        overall["tasks_completion_status"]["in_progress"] += 1

                        stats_by_project[project_id]["no_incomplete_tasks"] += 1
                        stats_by_project[project_id]["tasks_completion_status"]["in_progress"] += 1
                    else:
                        overall["tasks_completion_status"]["todo"] += 1
                        stats_by_project[project_id]["no_upcoming_tasks"] += 1

                        if task_info.completion_status == "not started":
                            stats_by_project[project_id]["no_incomplete_tasks"] += 1
                            stats_by_project[project_id]["tasks_completion_status"]["todo"] += 1
                        else:
                            stats_by_project[project_id]["tasks_completion_status"]["completed"] += 1

                if task_info.deadline:
                    current_date = datetime.now()
                    start_of_week = current_date - timedelta(days=current_date.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    deadline = task_info.deadline

                    if current_date > deadline and task_info.completion_status != "completed":
                        overall["no_overdue_tasks"] += 1
                        stats_by_project[project_id]["no_overdue_tasks"] += 1

                    if deadline >= start_of_week and deadline <= end_of_week:
                        day = deadline.weekday()
                        overall["no_due_this_week"][day] += 1
                        stats_by_project[project_id]["no_due_this_week"][day] += 1

            result = {
                "total": overall,
                **stats_by_project
            }

            return json.loads(json.dumps(result, default=str)), 200


        except Exception as e:
            print(e)
            return json.loads(json.dumps({"error": "Something went wrong while retrieving dashboard"}, default=str)), 500

# ----- END DASHBOARD ----- #
@app.before_request
def before_request_func():
    session_id = request.cookies.get('SESSION_ID')
    url = request.url
    method = request.method
    print(session_id)
    print(url)
    print(url == BASE_URL)
    if method != "OPTIONS" and "user_login" not in url \
        and "user_registration" not in url \
        and "user_logout" not in url \
        and "swagger" not in url\
        and url != BASE_URL:
        if session_id:
            user_session = Sessions.query.filter_by(session_id=session_id).first()
            if user_session:
                request.user = user_session.user_email
            else:
                return json.loads(json.dumps({"error": "Unauthorized request"}, default=str)), 401
        else:
            print("unauthorized")
            return json.loads(json.dumps({"error": "Unauthorized request"}, default=str)), 403


if __name__ == "__main__":
    app.run(debug=True, port=5000)
