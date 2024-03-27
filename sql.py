import sqlite3
from flask import Flask,jsonify,request
from flask_cors import CORS #,cross_origin 
from email.message import EmailMessage
import ssl
import smtplib
import os

app = Flask(__name__)
CORS(app)

db_filename = 'user.db'

if os.environ.get('ENV') == 'production':    
    db_path = os.path.join(os.getcwd(), db_filename)
else:    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_filename)


@app.route('/', methods=['GET'])
def hello():
    return jsonify({"responce": "This is MyApp"})

@app.route('/login', methods=['POST'])
def login():    
    # Login.js File Username & password
    data = request.json    
    username = data.get('username')
    password = data.get('password')
 
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Signup WHERE UserName=? AND Password=?', (username, password))
        result = cursor.fetchone()        

        if result is not None:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
            
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False})

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
@app.route('/sigin', methods=['POST','PUT'])
def sigin():
    # Sigin.js File Username & password & email
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Signup WHERE Username=? OR Email=?', (username, email))
        result = cursor.fetchone()

        if result:
            return jsonify({'success': False})
        else:                
            cursor.execute('INSERT INTO Signup (UserName, Password, Email) VALUES (?, ?, ?)', (username, password, email))
            conn.commit()
            return jsonify({'success': True})            
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False})
    
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/forgot', methods=['POST'])
def mail():
    # Sigin.js File Username & password & email
    data = request.json
    email = data.get('email')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Signup WHERE Email=?', (email,))
        result = cursor.fetchone()

        if result:
            column_names = [column[0] for column in cursor.description]
            password_index = column_names.index('Password')
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/data', methods=['GET','POST'])
def data():
    # Sigin.js File Username & password & email  
    # if request.method == 'GET':
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Signup')
        result = cursor.fetchall()            
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in result]                       
        if result:
            return jsonify(result)
        else:                                
            return jsonify([])                        
    except Exception as e:
        # print(f'Error: {e}')
        return jsonify({'Error': str(e)})

    finally:            
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # elif request.method == 'POST':
    #     pass  
    # else:
    #     return jsonify({'Error': 'Unsupported method'})
    
if __name__ == '__main__':
    app.run(debug=True)