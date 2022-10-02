from flask import Flask, render_template, request
import matplotlib,matplotlib.pyplot as plt
matplotlib.use('Agg')
import numpy as np

# Create App
app = Flask(__name__, template_folder='templates')

# Serve app in root
@app.route("/", methods=["GET", "POST"])

def push_to_server():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        # Get Inputs
        parameter_1 = request.form["ID"]
        parameter_2 = request.form["id_value"]

        # Read CSV and get Indexed Data
        (student_data, course_data) = get_data()

        if len(parameter_1) == 0 or len(parameter_2) == 0:
            # Return Error
            return render_template(
                "error.html"
            )

        elif parameter_1 == "student_id":
            try:
                # Calculate Total Marks
                total_marks = 0
                for i in student_data[int(parameter_2)]:
                    total_marks += i["marks"]
                
                # Render Template
                return render_template(
                    "student.html", 
                    parameter_2=int(parameter_2),
                    student_data = student_data, 
                    total_marks=total_marks
                )
            except:
                # Return Error
                return render_template(
                    "error.html"
                )
        elif parameter_1 == "course_id":
            try:
                # Calculate Average Marks
                total_marks = 0
                for i in course_data[int(parameter_2)]:
                    total_marks += i
                average_marks = total_marks / len(course_data[int(parameter_2)])

                # Calculate Maximum marks
                maximum_marks = max(course_data[int(parameter_2)])

                # Generate Histogram
                mark_array = np.array(course_data[int(parameter_2)])

                # Plot Histogram and save it as png
                plt.clf()
                plt.hist(mark_array)
                plt.xlabel("Marks")
                plt.ylabel("Frequency")
                plt.savefig(f"static/{parameter_2}.png")

                # Render Template
                return render_template(
                    "course.html",
                    parameter_2 = parameter_2,
                    average_marks=average_marks,
                    maximum_marks=maximum_marks
                )
            except:
                # Return Error
                return render_template(
                    "error.html"
                )
    else:
        # Return Error
        return render_template(
            "error.html"
        )

def get_data():
    # Read CSV
    f = open("data.csv", "r")
    f.readline()
    data = f.readlines()

    # Format Data
    for i in range(len(data)):
        if "\n" in data[i]:
            data[i] = data[i].replace("\n", "")

    # Create Student Dictionary, Index by Student_ID
    student_data = {}
    for i in range(len(data)):
        row = data[i].split(", ")
        student_data[int(row[0])] = []
    for i in range(len(data)):
        row = data[i].split(", ")
        student_data[int(row[0])].append({"course_id": int(row[1]), "marks": int(row[2])})


    # Create Course Dictionary, Index by Course_ID
    course_data = {}
    for i in range(len(data)):
        row = data[i].split(", ")
        course_data[int(row[1])] = []
    for i in range(len(data)):
        row = data[i].split(", ")
        course_data[int(row[1])].append(int(row[2]))
    
    f.close()

    return (student_data, course_data)


if __name__ == '__main__':
    app.run()