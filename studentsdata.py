from flask import Flask ,request,jsonify
import psycopg2
from psycopg2 import sql


app =Flask(__name__)


#database configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '1404'


def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database =DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection

def create_tb_if_not_exist():
    connection=get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS students_db( 
           student_id SERIAL PRIMARY KEY,
           studentname TEXT NOT NULL,
           rollno TEXT NOT NULL,
           course TEXT NOT NULL,
           coursecode TEXT NOT NULL       
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()
create_tb_if_not_exist()  


@app.route("/student_register", methods=['POST'])
def student_register():
    studentname = request.json['studentname']
    rollno= request.json['rollno']
    course = request.json['course']
    coursecode= request.json['coursecode']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
       INSERT INTO students_db(studentname, rollno, course, coursecode)
       VALUES (%s, %s, %s,%s)
 """,(studentname, rollno, course, coursecode))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "student registerd successfully"}),200
@app. route("/get_students", methods =['GET'])
def get_students():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            SELECT* FROM students_db;
""")
    students_db=cursor.fetchall()
    cursor.close()
    connection.close()
    result=[
      {"student_id":student[0],
       "studentname":student[1],"rollno":student[2],"course":student[3],"coursecode":student[4]} for student in students_db 
    ]
    return jsonify(result),200

@app.route('/student_update',methods=['PUT'])
def student_update():
    student_id = request.args['student_id']
    studentname = request.json['studentname']
    rollno= request.json['rollno']
    course = request.json['course']
    coursecode=request.json['coursecode']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            UPDATE students_db
                    SET studentname=%s, rollno=%s, course=%s,coursecode=%s where student_id=%s;
""",(studentname, rollno, course, coursecode, student_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "student updated successfully"}), 201
@app.route('/delete_student',methods=['DELETE'])
def delete_student():
    student_id=request.args.get('student_id')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            DELETE FROM students_db WHERE students_db=%s;
    """,(student_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "student deleted successfully"}), 200


if __name__ == '__main__':

    app.run(debug = True)
