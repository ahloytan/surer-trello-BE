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

# ----- Get Task By Task ID ----- #
get_task_parser = api.parser()
get_task_parser.add_argument("task_id", help="Enter task ID")
@api.route("/get_task")
@api.doc(description="Get task")
class GetTask(Resource):
    @api.expect(get_task_parser)
    def get(self):
        task_id = get_task_parser.parse_args().get("task_id")
        task_info = {}
        task_info[task_id] = {}
        for task in Task.query.filter_by(task_id=task_id):
            task_info[task_id]["project_id"] = task.json()["project_id"]
            task_info[task_id]["description"] = task.json()["description"]
            task_info[task_id]["position"] = task.json()["position"]
            task_info[task_id]["title"] = task.json()["title"]
            task_info[task_id]["completion_status"] = task.json()["completion_status"]
            created_datetime = task.json()["created_datetime"].strftime("%Y-%m-%d")
            print(task.json()["deadline"])
            if task.json()["deadline"] is None:
                deadline="<No due date entered>"
            else:
                deadline = task.json()["deadline"].strftime("%Y-%m-%d")
            task_info[task_id]["created_datetime"] = created_datetime
            task_info[task_id]["deadline"] = deadline
        if task_info != {}:
            return task_info, 200
        else:
            return "Failed", 400

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


# ----- Get user's task and team with user email ----- #
get_task_by_user_parser = api.parser()
get_task_by_user_parser.add_argument("email", help="Email of user")
@api.route("/get_team_and_task")
@api.doc(description="Get user's list of tasks for each project")
class GetTeamAndTask(Resource):
    @api.expect(get_task_by_user_parser)
    def get(self):
        email = get_task_by_user_parser.parse_args().get("email")
        team_task_dict = {}
        user_projects = Team.query.filter_by(user_email=email).all()
        for proj in user_projects:
            team_task_dict[int(proj.project_id)] = []
        tasks_from_user = Assignee.query.filter_by(user_email=email)
        for pid in team_task_dict.keys():
            for task in tasks_from_user:
                if int(task.project_id) == pid:
                    team_task_dict[pid].append(task.task_id)

        return team_task_dict, 200

# ------ Get user's projects and project_name --------
get_user_project_names = api.parser()
get_user_project_names.add_argument("email", help="Email of user")
@api.route("/get_user_project_names")
@api.doc(description="Get user's list of tasks for each project")
class getUserProjectNames(Resource):
    @api.expect(get_user_project_names)
    def get(self):
        email = get_task_by_user_parser.parse_args().get("email")
        user_projects_dict = {}
        user_projects = Team.query.filter_by(user_email=email).all()
        for proj in user_projects:
            user_projects_dict[int(proj.project_id)] = ""
        for pid in user_projects_dict.keys():
            p = Project.query.filter_by(project_id=pid).all()[0]
            user_projects_dict[pid] = p.description
        return user_projects_dict, 200


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
                        result = mailjet.send.create(data=data)
                        print(result)
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





if __name__ == "__main__":
    app.run(debug=True, port=5000)
