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

course_args = reqparse.RequestParser()
course_args.add_argument("course_name", type = str)
course_args.add_argument("course_code", type = str)
course_args.add_argument("course_description", type = str)

class Enrollment(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)

enrollment_args = reqparse.RequestParser()
enrollment_args.add_argument("course_id", type = int)

# API

# Student

class StudentAPI(Resource):
    def get(self, student_id):
        try:
            student = Student.query.get(student_id)
        except:
            return abort(500, message = "Internal server error")

        if student is not None:
            return {
                    "student_id": student.student_id,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "roll_number": student.roll_number
                }, 200
        else:
            return abort(404, message = "Student not found")

    
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
            return abort(409, message = "Student already exist")
        else:
            try:
                db.session.add(new_student)
            except:
                return abort(500, message = "Internal Server Error")
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
                }, 200
    
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
    
class CourseAPI(Resource):
    def get(self, course_id):
        try:
            course = Course.query.get(course_id)
        except:
            return abort(500, "Internal Server Error")
        else:
            if course is not None:
                return {
                            "course_id": course.course_id,
                            "course_name": course.course_name,
                            "course_code": course.course_code,
                            "course_description": course.course_description
                }, 200
            else:
                return abort(404, message = "Course not found")
    
    def post(self):
        args = course_args.parse_args()
        if args.get("course_name", None) == None:
            return {
                "error_code": "COURSE001",
                "error_message": "Course Name is required"
            }, 400
        elif args.get("course_code", None) == None:
            return {
                "error_code": "COURSE002",
                "error_message": "Course Code is required"
            }, 400

        new_course = Course(
            course_name = args["course_name"],
            course_code = args["course_code"],
            course_description = args["course_description"]
        )

        if Course.query.filter_by(course_code = args["course_code"]).first() is not None:
            return abort(409, message = "course_code already exist")
        else:
            try:
                db.session.add(new_course)
            except:
                return abort(500, "Internal Server Error")
            else:
                db.session.commit()
                return {
                            "course_id": new_course.course_id,
                            "course_name": new_course.course_name,
                            "course_code": new_course.course_code,
                            "course_description": new_course.course_description
                }, 201
    
    def put(self, course_id):
        old_course = Course.query.get(course_id)
        
        args = course_args.parse_args()

        if args.get("course_name", None) == None:
            return {
                "error_code": "COURSE001",
                "error_message": "Course Name is required"
            }, 400
        elif args.get("course_code", None) == None:
            return {
                "error_code": "COURSE002",
                "error_message": "Course Code is required"
            }, 400

        if old_course is None:
            return abort(404, message = "Course not found")

        old_course.course_name = args['course_name']
        old_course.course_code = args['course_code']
        old_course.course_description = args['course_description']

        if  Course.query.filter_by(course_code = old_course.course_code and course_id != old_course.course_id).first() is not None:
            return abort(409, message = "Course already exist")
        else:
            try:
                db.session.add(old_course)
            except:
                return abort(500, message = "Internal Server Error")
            else:
                db.session.commit()
                return {
                            "course_id": old_course.course_id,
                            "course_name": old_course.course_name,
                            "course_code": old_course.course_code,
                            "course_description": old_course.course_description
                }, 200
    
    def delete(self, course_id):
        old_course = Course.query.get(course_id)

        if old_course is None:
            return abort(404, message = "Course not found")
        
        try:
            db.session.delete(old_course)
        except:
            return abort(500, message = "Internal Server Error")
        else:
            db.session.commit()
            return "Successfully Deleted", 200

class EnrollmentAPI(Resource):
    def get(self, student_id):
        try:
            student = Student.query.get(student_id)
        except:
            return abort(500, message = "Internal server error")
        else:
            if student is None:
                return {
                            "error_code": "ENROLLMENT002",
                            "error_message": "Student does not exist."
                }, 400
        

            enrollment_list = Enrollment.query.filter_by(student_id = student_id).all()
            if enrollment_list == []:
                return abort(404, message = "Student is not enrolled in any course")
            
            json = []
            for enrollment in enrollment_list:
                json.append(
                    {
                        "enrollment_id": enrollment.enrollment_id,
                        "student_id": enrollment.student_id,
                        "course_id": enrollment.course_id
                    }
                )
            
            return json, 200
    
    def post(self, student_id):
        args = enrollment_args.parse_args()

        if args.get("course_id", None) == None:
            return {
                        "error_code": "ENROLLMENT001",
                        "error_message": "Course does not exist"
            }, 400
        else:
            try:
                course = Course.query.get(int(args["course_id"]))
            except:
                return abort(500, message = "Internal server error")
            else:
                if course is None:
                    return {
                            "error_code": "ENROLLMENT001",
                            "error_message": "Course does not exist"
                    }, 400 
        
        try:
            student = Student.query.get(student_id)
        except:
            return abort(500, message = "Internal server error")
        else:
            if student is None:
                return {
                            "error_code": "ENROLLMENT002",
                            "error_message": "Student does not exist."
                }, 400

        new_enrollment = Enrollment(
            student_id = student_id,
            course_id = args["course_id"]
        )

        enrollment = Enrollment.query.filter_by(student_id = student_id, course_id = args["course_id"]).all()

        if enrollment == []:
            return abort(404, message = "Enrollment already exists")

        try:
            db.session.add(new_enrollment)
        except:
            return abort(500, "Internal Server Error")
        else:
            db.session.commit()
            json = []
            json.append(
                {
                    "enrollment_id": new_enrollment.enrollment_id,
                    "student_id": new_enrollment.student_id,
                    "course_id": new_enrollment.course_id
                }
            )

            return json, 201
    
    def delete(self, student_id, course_id):
        try:
            course = Course.query.get(course_id)
        except:
            return abort(500, message = "Internal server error")
        else:
            if course is None:
                return {
                        "error_code": "ENROLLMENT001",
                        "error_message": "Course does not exist"
                }, 400
        
        try:
            student = Student.query.get(student_id)
        except:
            return abort(500, message = "Internal server error")
        else:
            if student is None:
                return {
                            "error_code": "ENROLLMENT002",
                            "error_message": "Student does not exist."
                }, 400
        
        enrollment = Enrollment.query.filter_by(student_id = student_id, course_id = course_id).all()

        if enrollment == []:
            return abort(404, message = "Enrollment for the student not found")
        
        try:
            db.session.delete(enrollment[0])
        except:
            return abort(500, message = "Internal Server Error")
        else:
            db.session.commit()
            return "Successfully deleted", 200




api.add_resource(StudentAPI, "/api/student", "/api/student/<int:student_id>")
api.add_resource(CourseAPI, "/api/course", "/api/course/<int:course_id>")
api.add_resource(EnrollmentAPI, "/api/student/<int:student_id>/course", "/api/student/<int:student_id>/course/<int:course_id>")

if __name__ == "__main__":
    app.run(
        debug=True
    )