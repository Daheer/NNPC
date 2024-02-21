from flask import Flask, Response, render_template, jsonify, request, redirect, url_for
import cv2
import numpy as np

app = Flask(__name__)

list_of_users = []
attendees = ['-'] * 100

@app.route('/', methods = ['POST', 'GET'])
def welcome():
    return render_template('home.html')

@app.route('/sign_in', methods = ['POST'])
def process_details():
    name = request.form['name']
    regNumber = request.form['regNumber']
    phoneNumber = request.form['phoneNumber']
    email = request.form['email']
    department = request.form['department']
    uniqueNumber = request.form['uniqueNumber']
    if int(uniqueNumber) <= 100 and attendees[int(uniqueNumber)] == '-':
        attendees[int(uniqueNumber)] = name
    return redirect(url_for('welcome'))
    
@app.route('/sign_in', methods = ['GET'])
def sign_in():
    return render_template('sign_in.html')

@app.route('/table', methods = ['GET'])
def view_table():
    return render_template('table.html', attendees = attendees)

@app.route('/home', methods=['GET', 'POST'], defaults={'user': 'Default User'})
@app.route('/home/<user>', methods=['GET', 'POST'])
def home(user):
    return f"<h1>This is the {user} for directory!<h1>"

# =================== SAVE THIS FOR LATER ===================
def generate_frames():
    for i in range(100):
        success, buffer = cv2.imencode('.jpg', np.random.rand(500, 500) * 255)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")
# =================== END OF SAVE THIS FOR LATER ===================

if __name__ == '__main__':
    app.run(debug=True)
