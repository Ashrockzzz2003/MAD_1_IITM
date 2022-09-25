from jinja2 import Template
import sys
import matplotlib.pyplot as plt
import numpy as np

TEMPLATE_ERROR = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Something Went Wrong</title>
</head>
<body>
    <h1>Wrong Inputs</h1>
    <p>Something went wrong</p>
</body>
</html>
"""

TEMPLATE_STUDENT_DATA = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Data</title>
</head>
<body>
    <h1>Student Details</h1>
    <table style="border: 1px solid black;">
        <thead>
            <tr>
                <th style="border: 1px solid black;">Student id</th>
                <th style="border: 1px solid black;">Course id</th>
                <th style="border: 1px solid black;">Marks</th>
            </tr>
        </thead>
        <tbody>
            {% for i in student_data[parameter_2] %}
            <tr>
                <td style="border: 1px solid black;">{{parameter_2}}</td>
                <td style="border: 1px solid black;">{{i["course_id"]}}</td>
                <td style="border: 1px solid black;">{{i["marks"]}}</td>
            </tr>
            {% endfor %}
            <tr>
                <td colspan="2" style="border: 1px solid black; text-align: center;">Total Marks</td>
                <td style="border: 1px solid black;">{{total_marks}}</td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""

TEMPLATE_COURSE_DATA = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Data</title>
</head>
<body>
    <h1>Course Details</h1>
    <table style="border: 1px solid black;">
        <thead>
            <tr>
                <th style="border: 1px solid black;">Average Marks</th>
                <th style="border: 1px solid black;">Maximum Marks</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid black;">{{average_marks}}</td>
                <td style="border: 1px solid black;">{{maximum_marks}}</td>
            </tr>
        </tbody>
    </table>
    <img src="{{parameter_2}}.png">
</body>
</html>
"""

def main():
    # Read Arguments
    parameter_1 = sys.argv[1]
    parameter_2 = sys.argv[2]

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

    if parameter_1 == "-s":
        try:
            # Calculate Total Marks
            total_marks = 0
            for i in student_data[int(parameter_2)]:
                total_marks += i["marks"]

            # Generate HTML
            student_details_content = Template(TEMPLATE_STUDENT_DATA).render(
                parameter_2=int(parameter_2),
                student_data = student_data, 
                total_marks=total_marks
            )

            # Create HTML file
            output = open("output.html", "w")
            output.write(student_details_content)
            output.close()
        except:
            student_details_content = Template(TEMPLATE_ERROR).render()
            output = open("output.html", "w")
            output.write(student_details_content)
            output.close()
    elif parameter_1 == "-c":
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
            
            plt.hist(mark_array)
            plt.xlabel("Marks")
            plt.ylabel("Frequency")
            plt.savefig(f"{parameter_2}.png")

            # Generate HTML
            course_details_content = Template(TEMPLATE_COURSE_DATA).render(
                parameter_2=parameter_2,
                average_marks=average_marks,
                maximum_marks=maximum_marks
            )

            # Create HTML File
            output = open("output.html", "w")
            output.write(course_details_content)
            output.close()
        except:
            student_details_content = Template(TEMPLATE_ERROR).render()
            output = open("output.html", "w")
            output.write(student_details_content)
            output.close()
    else:
        student_details_content = Template(TEMPLATE_ERROR).render()
        output = open("output.html", "w")
        output.write(student_details_content)
        output.close()
    
    f.close()

if __name__ == "__main__":
    main()
