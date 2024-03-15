from flask_app import app
from flask import render_template, redirect, flash, session, request
from flask_app.models.project import Project
from flask_app.models.student import Student
from flask_app.models.teacher import Teacher
from flask_app.models.event import Event
from .env import UPLOAD_FOLDER

from .env import ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import paypalrestsdk

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/events')
def events():
    if 'teacher_id' in session:
        return render_template('events.html', events = Event.get_all_event())
    if 'student_id' in session:
        return render_template('events.html', events = Event.get_all_event())
    return redirect('/')


@app.route('/events/new')
def addEvent():
    if 'teacher_id' in session:
        return render_template('addEvent.html')
    
    return redirect('/')


@app.route('/createevent', methods=['GET', 'POST'])
def create_event():
    if 'teacher_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'event_images' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['event_images']
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
                'title': request.form['title'],
                'description': request.form['description'],
                'deadline': request.form['deadline'],
                'event_images': filename,
                'teacher_id': session['teacher_id']
            }
    
    # Create the job using your Job class
            Event.create(data)
            return redirect(request.referrer)
    return redirect('/dashboard')

@app.route('/profilepic/student', methods=['POST'])
def new_profil_pic_user():
    if 'user_id' not in session:
        return redirect('/loginpage')
    data = {"id": session['user_id']}
    
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['image'] = filename
            Student.update_profile_pic_student(data)
    return redirect('/dashboardstudent')

@app.route('/event/<int:id>')
def viewEvent(id):
    if 'teacher_id' in session:
        data = {
            'teacher_id': session.get('teacher_id'),
            'id': id
        }
        loggedTeacher = Teacher.get_teacher_by_id(data)
        event = Event.get_event_by_idd(data)
        likes=Event.count_likes()
        studentWhoLikes = Event.get_students_who_liked_by_event_id(data)
        return render_template('event-detail.html', event=event, loggedTeacher=loggedTeacher,studentWhoLikes= studentWhoLikes,likes=likes)

    elif 'student_id' in session:
        data = {
            'student_id': session.get('student_id'),
            'id': id
        }
        loggedStudent  = Student.get_student_by_id(data)
        commenti=Event.get_comment_by_id(data)
        event = Event.get_event_by_idd(data)
        likes=Event.count_likes()
        studentWhoLikes = Event.get_students_who_liked_by_event_id(data)
        return render_template('event-detail.html', event=event, commenti=commenti,loggedStudent=loggedStudent,studentWhoLikes= studentWhoLikes,comments=Event.get_all_comments(),likes=likes)

    else:
        return redirect('/')

@app.route('/event/edit/<int:id>')
def editEvent(id):
    if 'teacher_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    event = Event.get_event_by_idd(data)
    if event and event['teacher_id'] == session['teacher_id']:
        return render_template('editEvent.html', event=event)
    return redirect('/')


@app.route('/event/update/<int:id>', methods = ['POST'])
def updateEvent(id):
    if 'teacher_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    event = Event.get_event_by_idd(data)
    if event and event['teacher_id'] == session['teacher_id']:
        if not Event.validate_eventUpdate(request.form):
            return redirect(request.referrer)
        data = {
            'description': request.form['description'],
            'title': request.form['title'],
            'deadline': request.form['deadline'],
            'id': id
        }
        Event.update(data)
        return redirect('/event/'+ str(id))
    return redirect('/')



@app.route('/event/delete/<int:id>')
def deleteEvent(id):
    if 'teacher_id' not in session:
        return redirect('/')
    data = {
        'id': id,
    }
    event = Event.get_event_by_idd(data)
    if event and event['teacher_id'] == session['teacher_id']:
        Event.delete_all_event_comments(data)
        Event.delete(data)
    return redirect('/events')

@app.route('/add/comment/<int:id>', methods = ['POST'])
def addComment(id):
    if 'student_id' not in session:
        return redirect('/')
    if len(request.form['comment'])<2:
        flash('The comment should be at least 2 characters', 'comment')
    data = {
        'comment': request.form['comment'],
        'student_id': session['student_id'],
        'event_id': id
    }
    Event.addComment(data)
    return redirect(request.referrer)

@app.route('/update/comment/<int:id>', methods = ['POST'])
def updateComment(id):
    if 'student_id' not in session:
        return redirect('/')
    if len(request.form['comment'])<2:
        flash('The comment should be at least 2 characters', 'comment')
    data = {
        'comment': request.form['comment'],
        'id': id
    }
    commenti = Event.get_comment_by_id(data)
    if commenti['student_id'] == session['student_id']:
        Event.update_comment(data)
    return redirect('/event/'+ str(commenti['event_id']))

@app.route('/delete/comment/<int:id>')
def deleteComment(id):
    if 'student_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    komenti = Event.get_comment_by_id(data)
    if komenti['student_id'] == session['student_id']:
        Event.delete_comment(data)
    return redirect(request.referrer)



@app.route('/edit/comment/<int:id>')
def editComment(id):
    if 'student_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    commenti = Event.get_comment_by_id(data)
    if commenti['student_id'] == session['student_id']:
        return render_template('editComment.html', commenti = commenti)
    return redirect('/')


@app.route('/add/like/<int:id>')
def addLike(id):
    if 'student_id' not in session:
        return redirect('/')
    data = {
        'event_id': id,
        'student_id': session['student_id']
    }
    studentWhoLikes = Event.get_students_who_liked_by_event_id(data)
    
    if session['student_id'] not in studentWhoLikes:
        Event.addLike(data)
    return redirect(request.referrer)

@app.route('/remove/like/<int:id>')
def removeLike(id):
    if 'student_id' not in session:
        return redirect('/')
    data = {
        'event_id': id,
        'student_id': session['student_id']
    }
    Event.removeLike(data)
    return redirect(request.referrer)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/error')
def error():
    return render_template('404-error.html')

@app.route('/classes')
def classes():
    return render_template('gallery.html')