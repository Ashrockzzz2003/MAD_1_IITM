import os
from flask import Flask, redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Setup App
# Should Change Config line!
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
    os.path.join(current_dir, "database.sqlite3")
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
@app.route("/", methods=["GET", "POST"])
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
        roll = request.form.get("roll")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        courses = request.form.getlist("courses")

        # Check if roll_number Already Exists
        if (Student.query.filter_by(roll_number=roll).first() == None):

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

            for course in courses:
                # Student_ID, Course_ID
                c_id = Course.query.get(int(course[7]))
                s_id = Student.query.filter_by(roll_number=roll).first()
                e_data = Enrollments(
                    estudent_id=s_id.student_id,
                    ecourse_id=c_id.course_id
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
            current_courses = Enrollments.query.filter_by(
                estudent_id=student_id).all()
            for i in range(len(current_courses)):
                current_courses[i] = int(current_courses[i].ecourse_id)

            return render_template(
                "update_student.html",
                current_id=current_data.student_id,
                current_roll=current_data.roll_number,
                current_fname=current_data.first_name,
                current_lname=current_data.last_name,
                current_courses=current_courses
            )
        elif request.method == "POST":
            updated_fname = request.form.get("f_name")
            updated_lname = request.form.get("l_name")
            updated_courses = request.form.getlist("courses")

            current_data.first_name = updated_fname
            current_data.last_name = updated_lname

            # Updating Enrollment

            # Flush Old records
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

            # Putting in New Records
            for course in updated_courses:
                # Student_ID, Course_ID
                c_id = Course.query.get(int(course[7]))
                s_id = student_id
                e_data = Enrollments(
                    estudent_id=s_id,
                    ecourse_id=c_id.course_id
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

# View Student Details


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
        enrollment_list.append([count, c_code, c_name, c_desc])

    return render_template(
        "view_student.html",
        student_list=student_list,
        enrollment_list=enrollment_list,
        courses=courses
    )


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True,
        port=8080
    )
