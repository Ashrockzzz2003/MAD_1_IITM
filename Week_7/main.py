import os
from flask import Flask, redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Setup App
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
    os.path.join(current_dir, "week7_database.sqlite3")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)


class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey(
        "student.student_id"), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey(
        "course.course_id"), nullable=False)

# Home Page


@app.route("/", methods=["GET"])
def index():
    student_list = Student.query.all()
    return render_template(
        "index.html",
        student_list=student_list
    )

# Add Student


@app.route("/student/create", methods=["GET", "POST"])
def add_student():
    if request.method == "GET":
        return render_template(
            "add_student.html"
        )
    elif request.method == "POST":

        # Get Inputs
        roll = request.form.get("roll")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")

        # If Student doesn't exist already
        if Student.query.filter_by(roll_number=roll).first() == None:
            # Insert Student Record
            data = Student(
                roll_number=roll,
                first_name=f_name,
                last_name=l_name
            )

            try:
                db.session.add(data)
            except:
                db.session.rollback()
                return render_template(
                    "exists.html"
                )
            else:
                db.session.commit()
                return redirect("/")
        else:
            return render_template(
                "exists.html"
            )

# Update Student


@app.route("/student/<int:student_id>/update", methods=["GET", "POST"])
def update_student(student_id):
    try:
        student_id = int(student_id)
        current_data = Student.query.get(student_id)

        if request.method == "GET":
            courses = Course.query.all()
            return render_template(
                "update_student.html",
                current_id=student_id,
                current_roll=current_data.roll_number,
                current_fname=current_data.first_name,
                current_lname=current_data.last_name,
                courses=courses
            )
        elif request.method == "POST":
            updated_fname = request.form.get("f_name")
            updated_lname = request.form.get("l_name")
            updated_course = request.form.get("course")

            # Update Name
            current_data.first_name = updated_fname
            current_data.last_name = updated_lname

            for data in Enrollments.query.filter_by(estudent_id=student_id):
                if data.ecourse_id == int(updated_course):
                    return render_template(
                        "exists.html"
                    )
                
            c_id = updated_course
            s_id = student_id
            e_data = Enrollments(
                estudent_id=s_id,
                ecourse_id=c_id
            )

            try:
                db.session.add(e_data)
            except:
                db.session.rollback()
                return render_template(
                    "exists.html"
                )
            else:
                db.session.commit()
    except:
        return render_template(
            "exists.html"
        )
    else:
        return redirect("/")

# Delete Student


@app.route("/student/<int:student_id>/delete")
def delete_student(student_id):
    student_id = int(student_id)
    student_data = Student.query.get(student_id)

    # Flush Enrollment records
    for data in Enrollments.query.filter_by(estudent_id=student_id):
        try:
            db.session.delete(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html"
            )
        else:
            db.session.commit()

    # Flush Out Student and Redirect

    try:
        db.session.delete(student_data)
    except:
        db.session.rollback()
        return render_template(
            "exists.html"
        )
    else:
        db.session.commit()
        return redirect("/")

# View Student


@app.route("/student/<int:student_id>")
def view_student(student_id):
    student_id = int(student_id)
    student_list = Student.query.filter_by(student_id=student_id)
    enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
    courses = Course.query.all()

    enrollment_list = []
    count = 0
    for enrollment in enrollments:
        count += 1
        c_id = enrollment.ecourse_id
        c_code = Course.query.filter_by(course_id=c_id).first().course_code
        c_name = Course.query.filter_by(course_id=c_id).first().course_name
        c_desc = Course.query.filter_by(
            course_id=c_id).first().course_description

        enrollment_list.append(
            {"count": count, "code": c_code, "name": c_name, "description": c_desc, "id": c_id})

    return render_template(
        "view_student.html",
        student_id=student_id,
        student_list=student_list,
        enrollment_list=enrollment_list,
        courses=courses
    )


# Remove Student Enrollment

@app.route("/student/<int:student_id>/withdraw/<int:course_id>", methods=["GET"])
def delete_enrollment(student_id, course_id):
    try:
        student_id = int(student_id)
        course_id = int(course_id)

        for data in Enrollments.query.filter_by(estudent_id=student_id, ecourse_id=course_id):
            try:
                db.session.delete(data)
            except:
                db.session.rollback()
                return render_template(
                    "exists.html"
                )
            else:
                db.session.commit()

    except:
        return (
            "exists.html"
        )
    else:
        return redirect("/")


@app.route("/courses", methods=["GET"])
def view_courses():
    course_list = Course.query.all()
    return render_template(
        "view_courses.html",
        course_list=course_list
    )


@app.route("/course/create", methods=["GET", "POST"])
def add_course():
    try:
        if request.method == "GET":
            return render_template(
                "add_course.html"
            )
        elif request.method == "POST":
            code = request.form.get("code")
            c_name = request.form.get("c_name")
            desc = request.form.get("desc")

            data = Course(
                course_code=code,
                course_name=c_name,
                course_description=desc
            )

            try:
                db.session.add(data)
            except:
                db.session.rollback()
                return render_template(
                    "exists_2.html"
                )
            else:
                db.session.commit()
    except:
        return render_template(
            "exists_2.html"
        )
    else:
        return redirect("/courses")


@app.route("/course/<int:course_id>/update", methods=["GET", "POST"])
def update_course(course_id):
    try:
        course_id = int(course_id)
        data = Course.query.get(course_id)

        if request.method == "GET":
            return render_template(
                "update_course.html",
                data=data,
                course_id=course_id
            )
        elif request.method == "POST":
            c_name = request.form.get("c_name")
            desc = request.form.get("desc")

            # Update in Course Table
            data.course_name = c_name
            data.course_description = desc

            try:
                db.session.commit()

            except:
                db.session.rollback()
                return render_template(
                    "exists_2.html"
                )
            else:
                return redirect("/courses")

    except:
        return render_template(
            "exists_2.html"
        )

# Delete a Course


@app.route("/course/<int:course_id>/delete", methods=["GET", "POST"])
def delete_course(course_id):
    course_id = int(course_id)
    course_data = Course.query.get(course_id)

    # Flush Enrollment records
    for data in Enrollments.query.filter_by(ecourse_id=course_id):
        try:
            db.session.delete(data)
        except:
            db.session.rollback()
            return render_template(
                "exists_2.html"
            )
        else:
            db.session.commit()

    # Flush Out Course and Redirect
    try:
        db.session.delete(course_data)
    except:
        db.session.rollback()
        return render_template(
            "exists_2.html"
        )
    else:
        db.session.commit()
        return redirect("/")

# View Course Details


@app.route("/course/<int:course_id>", methods=["GET", "POST"])
def view_course(course_id):
    try:
        course_id = int(course_id)

        course_data = Course.query.get(course_id)
        student_list = []
        for data in Enrollments.query.filter_by(ecourse_id=course_id).all():
            student_list.append(data.estudent_id)

        student_data = []

        count = 0
        for student in student_list:
            count += 1
            students = Student.query.get(student)
            student_data.append({"count": count, "roll_number": students.roll_number,
                                "f_name": students.first_name, "l_name": students.last_name})

        return render_template(
            "view_course.html",
            student_data=student_data,
            course_data=course_data
        )

    except:
        return render_template(
            "exists_2.html"
        )


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True,
        port=5000
    )
