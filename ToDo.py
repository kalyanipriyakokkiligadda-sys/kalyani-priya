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
       CREATE TABLE IF NOT EXISTS ToDo_db( 
           task_id SERIAL PRIMARY KEY,
           title TEXT NOT NULL,
           description TEXT NOT NULL,
           duedate TEXT NOT NULL,
           prirority TEXT DEFAULT medium,
           status TEXT DEFAULT pending        
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()
create_tb_if_not_exist()  


@app.route("/create_task", methods=['POST'])
def create_task():
    title= request.json['title']
    description= request.json['description']
    duedate = request.json['duedate']
    prirority= request.json['prirority']
    status=request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
       INSERT INTO ToDo_db(title, description, duedate,prirority,status)
       VALUES (%s, %s, %s,%s,%s)
 """,(title, description, duedate,prirority,status))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "task registerd successfully"}),200
@app. route("/get_task", methods =['GET'])
def get_task():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            SELECT* FROM ToDo_db;
""")
    ToDo_db=cursor.fetchall()
    cursor.close()
    connection.close()
    result=[
      {"task_id":task[0],
       "title":task[1],"description":task[2],"duedate":task[3],"prirority":task[4],"status":task[5]} for task in ToDo_db 
    ]
    return jsonify(result),200

@app.route('/update_task',methods=['PUT'])
def update_task():
    task_id = request.args['task_id']
    title = request.json['title']
    description= request.json['description']
    duedate = request.json['duedate']
    prirority=request.json['prirority']
    status=request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            UPDATE ToDo_db
                    SET title=%s, description=%s, duedate=%s,prirority=%s,status=%s where task_id=%s;
""",(title, description, duedate,prirority,status,task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "task updated successfully"}), 201

@app.route('/update_status',methods=['PUT'])
def update_status():
    task_id = request.args['task_id']
    status=request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            UPDATE ToDo_db
                    SET status=%s where task_id=%s;
""",(status,task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "status updated successfully"}), 201



@app.route('/task_delete',methods=['DELETE'])
def task_delete():
    task_id=request.args.get('task_id')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            DELETE FROM ToDo_db WHERE ToDo_db=%s;
    """,(task_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "task deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug = True)