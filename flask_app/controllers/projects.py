
from flask_app import app

from flask import render_template, redirect, session, request, flash,url_for


from flask_app.models.project import Project
from flask_app.models.student import Student
from flask_app.models.teacher import Teacher

from .env import UPLOAD_FOLDER
from .env import UPLOAD_FOLDER_LOGOS
from .env import ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['job_images_logo'] = UPLOAD_FOLDER_LOGOS
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import paypalrestsdk

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/projects')
def projects():
    return render_template('dashboard.html')


@app.route('/postaprojects')
def postaproject():
    if 'student_id' not in session:
        return redirect('/')
    loggedStudentData = {
        'student_id': session['student_id']
    }
    return render_template('postaprojects.html',loggedStudent =Student.get_student_by_id(loggedStudentData))


@app.route('/createproject', methods=['POST'])
def create_project():
    if 'student_id' not in session:
        return redirect('/')

    images = request.files.getlist('job_post_image')
    image_filenames = []

    for image in images:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename
            filename = time
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filenames.append(filename)

    # Get the company logo image and save it
    logos = request.files.getlist('company_logo')
    logo_filenames = []

    for logo in logos:
        if logo and allowed_file(logo.filename):
            filename = secure_filename(logo.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename
            filename = time
            logo.save(os.path.join(app.config['job_images_logo'], filename))
            logo_filenames.append(filename)

    # Construct the data dictionary for creating the job
    data = {
        'title': request.form['title'],
        'description': request.form['description'],
        'job_post_image': ','.join(image_filenames),
        'student_id': session['student_id']
    }
    
    # Create the job using your Job class
    Project.create_project(data)

    return redirect('/dashboardStudent')


@app.route('/project/<int:id>')
def viewproject(id):
    if 'student_id' in session:
        data = {
            'student_id': session.get('student_id'),
            'project_id': id
        }
        loggedStudent = Student.get_student_by_id(data)
        project = Project.get_project_by_id(data)
        
        return render_template('event-detail.html', project=project, loggedStudent=loggedStudent)

    elif 'teacher_id' in session:
        data = {
            'teacher_id': session.get('costumer_id'),
            'project_id': id
        }
        loggedTeacher = Teacher.get_teacher_by_id(data)
        loggedStudent = Student.get_student_by_id(data)
        project = Project.get_project_by_id(data)
        
        return render_template('event-detail.html', project=project, loggedStudent=loggedStudent, loggedTeacher=loggedTeacher)

    else:
        return redirect('/')
    
@app.route('/all_professions')
def view_all_professions():
    professions = Provider.get_all_professions()
    return render_template('dashboard.html', professions=professions)

@app.route('/job/edit/<int:id>')
def editJob(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session.get('provider_id'),
        'job_id': id
    }
    job = Job.get_job_by_id(data)
    if job and job['provider_id'] == session['provider_id']:
        return render_template('editjob.html', job=job)
    return redirect('/dashboarProvider')


@app.route('/job/update/<int:id>', methods = ['POST'])
def updateJob(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session.get('provider_id'),
        'job_id': id
    }
    job = Job.get_job_by_id(data)
    if job and job['provider_id'] == session['provider_id']:
        data = {
            'description': request.form['description'],
            'address': request.form['address'],
            'education_experience': request.form['education_experience'],
            'city': request.form['city'],
            'experience': request.form['experience'],
            'employment_status': request.form['employment_status'],
            'id': id
        }
        Job.update(data)
        return redirect('/job/'+ str(id))
    return redirect('/dashboarProvider')



@app.route('/job/delete/<int:id>')
def deleteJob(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'job_id': id
    }
    Job.delete(data)
    return redirect(request.referrer)

@app.route('/rate_job/<int:job_id>', methods=['POST'])
def rate_job(job_id):
    if 'costumer_id' not in session:
        return redirect('/')
    
    if 'provider_id' in session:
        return redirect('/logout')

    rating = int(request.form.get('rating', 0))

    if 1 <= rating <= 5:
        Job.update_star_rating(job_id, rating)
        flash('Rating submitted successfully!', 'success')
    else:
        flash('Invalid rating value. Please choose a value between 1 and 5.', 'error')

    return redirect('/dashboard')
@app.route('/checkout/paypal')
def checkoutPaypal():
    if 'costumer_id' not in session:
            return redirect('/')
    cmimi = 100
    ora = 2
    totalPrice = round(cmimi * ora)

    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AfJFDDdf4p2iTRu7AUMcyC3G7D9rOJL26DqChJ3SnGuKIzIKNnzRQ6Xy7bjZG-MQNwgoSQrPOBDhL9x0",
            "client_secret": "EHfue1ecmGryKAy9qYp9S1yjNG5HloMaJItptFCqooNUuRGc0wvZz9fv5WoYq-KFJAwpYIgvJCvYF23m"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": totalPrice,
                    "currency": "USD"  # Adjust based on your currency
                },
                "description": f"Pagese per kontaktin {ora} orë!"
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccess', _external=True, totalPrice=totalPrice),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)






@app.route("/success", methods=["GET"])
def paymentSuccess():
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AfJFDDdf4p2iTRu7AUMcyC3G7D9rOJL26DqChJ3SnGuKIzIKNnzRQ6Xy7bjZG-MQNwgoSQrPOBDhL9x0",
            "client_secret": "EHfue1ecmGryKAy9qYp9S1yjNG5HloMaJItptFCqooNUuRGc0wvZz9fv5WoYq-KFJAwpYIgvJCvYF23m"
        })
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            
            
            ammount = request.args.get('totalPrice')
            status = 'Paid'
            job_id = session['costumer_id']
            data = {
                'ammount': ammount,
                'status': status,
                'job_id': job_id
            }
            Job.createPayment(data)
           
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/dashboard')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/dashboard')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/dashboard')


@app.route("/cancel", methods=["GET"])
def paymentCancel():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/dashboard')