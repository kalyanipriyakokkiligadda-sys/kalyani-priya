from flask import Flask ,request,jsonify
import psycopg2
from flask_bcrypt import Bcrypt


app =Flask(__name__)

bcrypt=Bcrypt(app)

# database configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '1404'

# Database connection Function
def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database =DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection
# Create table If Not Exists
def create_tb_if_not_exist():
    connection=get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS user_data( 
           user_id SERIAL PRIMARY KEY,
           username TEXT NOT NULL,
           password TEXT NOT NULL,
           email TEXT NOT NULL UNIQUE                        
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()
create_tb_if_not_exist()  


@app.route("/signup", methods=['POST'])
def signup():
    username=request.json['username']
    password=request.json['password']
    email=request.json['email']

    hashed_password=bcrypt.generate_password_hash(password).decode('utf-8')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
       INSERT INTO user_data(username, password, email)
       VALUES (%s, %s, %s)
 """,(username, hashed_password, email))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "user signup successfully"}),201

@app.route("/login",methods=['POST'])
def login():
    email=request.json['email'] 
    password=request.json['password']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
         SELECT user_id,username, password
        FROM user_data WHERE email=%s
    """,(email,))

    user=cursor.fetchone()
    cursor.close()
    connection.close()

    if user is None:
        return jsonify({"error":"user not found"}),404
    user_id,username, hashed_password=user

    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({"error":"Invalid password"}),401
    return jsonify({
        "message":"Login successful",
        "user": {
            "user_id":user_id,
            "username":username,
            "email":email,
            "password":hashed_password
        }
    }),200              
if __name__ == '__main__':
    app.run(debug = True)