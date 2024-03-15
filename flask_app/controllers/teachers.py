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

# Employee Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/loginPage')
def loginPage():
    if 'teacher_id' in session:
        return redirect('/dashboard')
    return render_template('loginTeacher.html')

@app.route('/login', methods=['POST'])
def login():
    if 'teacher_id' in session:
        return redirect('/dashboard')
    teacher = Teacher.get_teacher_by_email(request.form)
    if not teacher:
        flash('This email does not exist.', 'emailLogin')
        return redirect('/loginPage')
    if not bcrypt.check_password_hash(teacher['password'], request.form['password']):
        flash('Your password is wrong!', 'passwordLogin')
        return redirect('/loginPage')
    session['teacher_id'] = teacher['id']
    return redirect('/dashboard')

@app.route('/registerTeacher')
def registerPageTeacher():
    if 'teacher_id' in session:
        return redirect('/dashboardTeacher')
    return render_template('registerTeacher.html')


@app.route('/registerTeacher', methods=['POST'])
def register():
    if 'teacher_id' in session:
        return redirect('/dashboard')
    
    if Teacher.get_teacher_by_email(request.form):
        flash('This email already exists. Try another one.', 'emailSignUp')
        return redirect('/loginPage')
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
        'password': bcrypt.generate_password_hash(request.form['password']),
        'verification_code': verificationCode,
    }
    
    Teacher.create_teacher(data)
    
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
    
    teacher = Teacher.get_teacher_by_email(data)
    
    session['teacher_id'] = teacher['id']

    return redirect('/verify/email')

@app.route('/verify/email')
def verifyEmail():
    if 'teacher_id' not in session:
        return redirect('/')
    data = {
        'teacher_id': session['teacher_id']
    }
    teacher = Teacher.get_teacher_by_id(data)
    if teacher['is_verified'] == 1:
        return redirect('/dashboard')
    return render_template('verify.html', loggedTeacher = teacher)


@app.route('/activate/account', methods=['POST'])
def activateAccount():
    if 'teacher_id' not in session:
        return redirect('/')
    data = {
        'teacher_id': session['teacher_id']
    }
    teacher = Teacher.get_teacher_by_id(data)
    if teacher['is_verified'] == 1:
        return redirect('/dashboard')
    
    if not request.form['verification_code']:
        flash('Verification Code is required', 'wrongCode')
        return redirect(request.referrer)
    
    if int(request.form['verification_code']) != int(teacher['verification_code']):
        string = '0123456789'
        vCode = ""
        length = len(string)
        for i in range(8) :
            vCode += string[math.floor(random.random() * length)]
        verificationCode = vCode
        dataUpdate = {
            'verification_code': verificationCode,
            'teacher_id': session['teacher_id']
        }
        Teacher.updateVerificationCode(dataUpdate)
        LOGIN = ADMINEMAIL
        TOADDRS  = teacher['email']
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
    
    Teacher.activateAccount(data)
    return redirect('/dashboard')



@app.route('/dashboard')
def dashboard():
    if 'teacher_id' not in session:
        return redirect('/loginPage')
    if 'student_id' in session:
        return redirect('/logout')
    loggedTeacherData = {
        'teacher_id': session['teacher_id'],
         
    } 
    
    loggedTeacher = Teacher.get_teacher_by_id(loggedTeacherData)
    project = Project.get_all_projects()
    projectposted=Project.count_projects()
    events=Event.get_all_event()
    if not loggedTeacher:
        return redirect('/logout')
  
    return render_template('dashboard.html',project=project, projectposted=projectposted,events=events)

@app.route('/results', methods=['GET', 'POST'])
def search():
    if 'teacher_id' not in session:
        return redirect('/')

    search_query = request.args.get('searchfield', default='')

    projects = []

    if search_query:
        projects = Project.search(search_query)
    return render_template('results.html', projects=projects)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



