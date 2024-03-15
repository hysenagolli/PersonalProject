from flask_app import app
from flask import render_template, redirect, session, request, flash
import random
import math
import smtplib
from .env import ADMINEMAIL
from .env import PASSWORD
from flask_app.models.teacher import Teacher
from flask_app.models.student import Student
from flask_app.models.project import Project
from flask_app.models.event import Event
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
from .env import UPLOAD_FOLDER

from .env import ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# HR Routes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/loginPageStudent')
def loginPageStudent():
    if 'student_id' in session:
        return redirect('/dashboardStudent')
    return render_template('loginStudent.html')

@app.route('/loginStudent', methods=['POST'])
def loginStudent():
    if 'student_id' in session:
        return redirect('/dashboardStudent')
    student = Student.get_student_by_email(request.form)
    if not student:
        flash('This email does not exist.', 'emailLoginStudent')
        return redirect('/loginPageStudent')
    if not bcrypt.check_password_hash(student['password'], request.form['password']):
        flash('Your password is wrong!', 'passwordLoginStudetn')
        return redirect('/loginPageStudent')
    session['student_id'] = student['id']
    return redirect('/dashboardStudent')

@app.route('/registerStudent')
def registerPageStudent():
    if 'student_id' in session:
        return redirect('/dashboardStudent')
    return render_template('registerStudent.html')


@app.route('/registerStudent', methods=['POST'])
def registerStudent():
    if 'student_id' in session:
        return redirect('/dashboardStudent')
    
    if Student.get_student_by_email(request.form):
        flash('This email already exists. Try another one.', 'emailSignUpStudent')
        return redirect('/loginPageStudent')
    string = '0123456789'
    vCode = ""
    length = len(string)
    for i in range(8) :
        vCode += string[math.floor(random.random() * length)]
    verificationCode = vCode

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'class_name': request.form['class_name'],
        'about': request.form['about'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'verification_code': verificationCode,
    }
    
    Student.create_student(data)
    
    LOGIN = ADMINEMAIL
    TOADDRS  = request.form['email']
    SENDER = ADMINEMAIL
    SUBJECT = 'Verify Your Email'
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
        % ((SENDER), "".join(TOADDRS), SUBJECT) )
    msg += f'Use this verification code to activate your account: {verificationCode}'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(LOGIN, PASSWORD)
    server.sendmail(SENDER, TOADDRS, msg)
    server.quit()
    
    student = Student.get_student_by_email(data)
    
    session['student_id'] = student['id']

    return redirect('/verify/email/student')

@app.route('/verify/email/student')
def verifyEmailStudent():
    if 'student_id' not in session:
        return redirect('/')
    data = {
        'student_id': session['student_id']
    }
    student = Student.get_student_by_id(data)
    if student['is_verified'] == 1:
        return redirect('/dashboardStudent')
    return render_template('verifyStudent.html', loggedStudent = student)


@app.route('/activate/account/student', methods=['POST'])
def activateAccountStudent():
    if 'student_id' not in session:
        return redirect('/')
    data = {
        'student_id': session['student_id']
    }
    student = Student.get_student_by_id(data)
    if student['is_verified'] == 1:
        return redirect('/dashboardStudent')
    
    if not request.form['verification_code']:
        flash('Verification Code is required', 'wrongCode')
        return redirect(request.referrer)
    
    if int(request.form['verification_code']) != int(student['verification_code']):
        string = '0123456789'
        vCode = ""
        length = len(string)
        for i in range(8) :
            vCode += string[math.floor(random.random() * length)]
        verificationCode = vCode
        dataUpdate = {
            'verification_code': verificationCode,
            'student_id': session['student_id']
        }
        Student.updateVerificationCode(dataUpdate)
        LOGIN = ADMINEMAIL
        TOADDRS  = student['email']
        SENDER = ADMINEMAIL
        SUBJECT = 'Verify Your Email'
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
            % ((SENDER), "".join(TOADDRS), SUBJECT) )
        msg += f'Use this verification code to activate your account: {verificationCode}'
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(LOGIN, PASSWORD)
        server.sendmail(SENDER, TOADDRS, msg)
        server.quit()

        flash('Verification Code is wrong. We just sent you a new one', 'wrongCode')
        return redirect(request.referrer)
    
    Student.activateAccount(data)
    return redirect('/dashboardStudent')



@app.route('/dashboardStudent')
def dashboardStudent():
    if 'student_id' not in session:
        return redirect('/loginPageStudent')
    
    if 'teacher_id' in session:
        return redirect('/logout')
    loggedStudentData = {
        'student_id': session['student_id']
    } 
    project = Project.get_project_by_id(loggedStudentData)
    loggedStudent = Student.get_student_by_id(loggedStudentData)
    projects=Project.get_student_project_by_id(loggedStudentData)
    if not loggedStudent:
        return redirect('/logoutStudent')
    return render_template('dashboardStudent.html', projects=projects,project=project)

@app.route('/logoutStudent')
def logoutStudent():
    session.clear()
    return redirect('/')

@app.route('/createproject', methods=['GET', 'POST'])
def createproject():
    if 'student_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file_post' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file_post']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename
            filename = time
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Construct the data dictionary for creating the job
            data = {
                
                'file_post': filename,
                'student_id': session['student_id']
            }
    
    # Create the job using your Job class
            Student.createproject(data)
            return redirect(request.referrer)
    return redirect(request.referrer)