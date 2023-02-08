import os
from flask import Flask
from flask_restful import Resource, Api, abort, reqparse, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(
    current_dir, "api_database.sqlite3"
)

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

# API init
api = Api(app)

CORS(app)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)

student_args = reqparse.RequestParser()
student_args.add_argument("first_name", type = str)
student_args.add_argument("roll_number", type = str)
student_args.add_argument("last_name", type = str)

class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    course_name = db.Column(db.String, nullable = False)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_description = db.Column(db.String)

class Enrollment(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)

# API

# Student

class StudentAPI(Resource):
    def get(self, student_id):
        try:
            student = Student.query.get(student_id)
        except:
            abort(500, message = "Internal server error")

        if student is not None:
            return {
                    "student_id": student.student_id,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "roll_number": student.roll_number
                }, 200
        else:
            abort(404, message = "Student not found")

    
    def post(self):
        args = student_args.parse_args()

        if args.get("roll_number", None) == None:
            return {
                "error_code": "STUDENT001",
                "error_message": "Roll Number required"
            }, 400
        elif args.get("first_name", None) == None:
            return {
                "error_code": "STUDENT002",
                "error_message": "First Name is required"
            }, 400

        new_student = Student(
            roll_number = args['roll_number'],
            first_name = args['first_name'],
            last_name = args['last_name']
        )

        if Student.query.filter_by(roll_number = new_student.roll_number).first() is not None:
            abort(409, message = "Student already exist")
        else:
            try:
                db.session.add(new_student)
            except:
                abort(500, message = "Internal Server Error")
            else:
                db.session.commit()
                return {
                    "student_id": new_student.student_id,
                    "first_name": new_student.first_name,
                    "last_name": new_student.last_name,
                    "roll_number": new_student.roll_number
                }, 201

    def put(self, student_id):
        old_student = Student.query.get(student_id)
        
        args = student_args.parse_args()

        if args.get("roll_number", None) == None:
            return {
                "error_code": "STUDENT001",
                "error_message": "Roll Number required"
            }, 400
        elif args.get("first_name", None) == None:
            return {
                "error_code": "STUDENT002",
                "error_message": "First Name is required"
            }, 400

        if old_student is None:
            return abort(404, message = "Student not found")

        old_student.roll_number = args['roll_number']
        old_student.first_name = args['first_name']
        old_student.last_name = args['last_name']

        if  Student.query.filter_by(roll_number = old_student.roll_number and student_id != old_student.student_id).first() is not None:
            return abort(409, message = "Student already exist")
        else:
            try:
                db.session.add(old_student)
            except:
                return abort(500, message = "Internal Server Error")
            else:
                db.session.commit()
                return {
                    "student_id": old_student.student_id,
                    "first_name": old_student.first_name,
                    "last_name": old_student.last_name,
                    "roll_number": old_student.roll_number
                }, 201
    
    def delete(self, student_id):
        old_student = Student.query.get(student_id)

        if old_student is None:
            return abort(404, message = "Student not found")
        
        try:
            db.session.delete(old_student)
        except:
            return abort(500, message = "Internal Server Error")
        else:
            db.session.commit()
            return "Successfully Deleted", 200
    


api.add_resource(StudentAPI, "/api/student", "/api/student/<int:student_id>")

if __name__ == "__main__":
    app.run(
        debug=True
    )