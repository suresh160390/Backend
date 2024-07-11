from flask import Flask,jsonify,request,send_from_directory
from flask_cors import CORS #,cross_origin 
from email.message import EmailMessage
import ssl
import smtplib
import os
import psycopg2
from dotenv import load_dotenv


app = Flask(__name__,static_folder='build',static_url_path='/')
CORS(app)

load_dotenv()

user_name = os.getenv('user_name')
pass_word = os.getenv('pass_word')
db_loc = os.getenv('db_loc')
db_name = os.getenv('db_name')

conn = psycopg2.connect(
dbname=db_name,
user=user_name,
password=pass_word,
host=db_loc
)

# if os.environ.get('ENV') == 'production':    
#     db_path = os.path.join(os.getcwd(), db_filename)
# else:    
#     db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_filename)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# @app.route('/', methods=['GET'])
# def hello():
#     return jsonify({"responce": "This is MyApp"})

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/login', methods=['POST'])
def login():    
    # Login.js File Username & password
    data = request.json    
    username = data.get('username')
    password = data.get('password')
 
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Signup" WHERE Username=%s AND Password=%s', (username, password))
        result = cursor.fetchone()        

        if result is not None:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
            
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False})

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
    
@app.route('/sigin', methods=['POST','PUT'])
def sigin():
    # Sigin.js File Username & password & email
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    try:
        cursor = conn.cursor()       
        cursor.execute('SELECT * FROM "Signup" WHERE Username=%s OR Email=%s', (username, email))
        result = cursor.fetchone()

        if result:
            return jsonify({'success': False})
        else:                
            cursor.execute('INSERT INTO "Signup" (Username, Password, Email) VALUES (%s, %s, %s)', (username, password, email))
            conn.commit()
            return jsonify({'success': True})            
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False})
    
    finally:        
        if 'cursor' in locals() and cursor:
            cursor.close()

@app.route('/forgot', methods=['POST'])
def mail():
    # Sigin.js File Username & password & email
    data = request.json
    email = data.get('email')
    
    try:       
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Signup" WHERE Email=%s', (email,))
        result = cursor.fetchone()

        if result:
            column_names = [column[0] for column in cursor.description]
            password_index = column_names.index('password')
            mail_password=result[password_index]       
            email_sender='suresha003@gmail.com'  #'suresha16031990@gmail.com'
            email_password='cjru cepx vvsz fxfg'   # create App password on your gmail Account, Security, 2-Step Verification, App password click & Create
            email_receiver=email.lstrip().rstrip()
            # print(type(email_receiver))

            subject = 'Password Recovery'
            body = f'Your password is: {mail_password}'

            em=EmailMessage()              
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            
            em.set_content(body)
            contex=ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com",465,context=contex) as smtp:
                smtp.login(email_sender,email_password)
                smtp.sendmail(email_sender,email_receiver,em.as_string())
    
            return jsonify({'success': True})
        else:                               
            return jsonify({'success': False})            
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False})
    
    finally:        
        if 'cursor' in locals() and cursor:
            cursor.close()

@app.route('/data', methods=['GET','POST'])
def data():
    # Sigin.js File Username & password & email  
    # if request.method == 'GET':
    try:        
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Signup"')
        result = cursor.fetchall()                  
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in result]                       
        # print(result)  
        if result:
            return jsonify(result)
        else:                                
            return jsonify([])                        
    except Exception as e:
        # print(f'Error: {e}')
        return jsonify({'Error': str(e)})

    finally:            
        if 'cursor' in locals() and cursor:
            cursor.close()   

# user_name = 'root'
# pass_word = '0fLj9dLurXT3aOJyP1FPMtuyMm68a1ll'
# db_loc = 'dpg-cq7q6vmehbks73942220-a.oregon-postgres.render.com'
# db_name = 'suresh'

# conn = psycopg2.connect(
# dbname=db_name,
# user=user_name,
# password=pass_word,
# host=db_loc
# )

# cur = conn.cursor()

# create_table_query = '''CREATE TABLE "Signup"(
#                      id SERIAL PRIMARY KEY,
#                     Username VARCHAR(50),
#                     Password VARCHAR(50),
#                     Email VARCHAR(50));'''

# cur.execute(create_table_query)

# print("Table created successfully")

# conn.commit()

# cur.close()
# conn.close()


# conn = psycopg2.connect(
# dbname='suresh',
# user='root',
# password='0fLj9dLurXT3aOJyP1FPMtuyMm68a1ll',
# host='dpg-cq7q6vmehbks73942220-a.oregon-postgres.render.com'
# )

# cursor = conn.cursor()
# # insert_data_query = '''INSERT INTO "Signup" (Username, Password, Email) VALUES (%s, %s, %s)'''
# cursor.execute('INSERT INTO "Signup" (UserName, Password, Email) VALUES (%s, %s, %s)', ('suresh', 'suresh@123', 'suresh003@gmail.com'))
# # data = ('loga', 'loga@123', 'loga003@gmail.com')
# # cursor.execute(insert_data_query, data)
# print("Data inserted successfully")

# conn.commit()

# cursor.close()
# conn.close()

if __name__ == '__main__':
    app.run(debug=True)
