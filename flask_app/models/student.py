from flask_app.config.mysqlconnection import connectToMySQL
import re	# the regex module
from flask import flash  
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
class Student:
    db_name = 'projectsdb'
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.class_name = data['class_name']
        self.email = data['email']
        self.about = data['about']
        self.is_verified = data['is_verified']
        self.verification_code = data['verification_code']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_student_by_email(cls, data):
        query = 'SELECT * FROM students WHERE email= %(email)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def get_all_class_names(cls):
        query = 'SELECT DISTINCT class_name FROM students;'
        results = connectToMySQL(cls.db_name).query_db(query)
        class_names = [result['student'] for result in results]
        return class_names

    @classmethod
    def get_student_by_id(cls, data):
        query = 'SELECT * FROM students WHERE id= %(student_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
        
    @classmethod
    def updateVerificationCode(cls, data):
        query = "UPDATE students SET verification_code = %(verification_code)s WHERE students.id = %(student_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def activateAccount(cls, data):
        query = "UPDATE students set is_verified = 1 WHERE students.id = %(student_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def createproject(cls, data):
        query = "UPDATE students SET file_post = %(image)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)  
    
    @classmethod
    def create_student(cls, data):
        query = "INSERT INTO students (first_name, last_name, class_name, email, password, about, verification_code) VALUES ( %(first_name)s, %(last_name)s, %(class_name)s,%(email)s,%(password)s,%(about)s, %(verification_code)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update_student(cls, data):
        query = "UPDATE students SET first_name = %(first_name)s, last_name = %(last_name)s, class_name=%(class_name)s, email= %(email)s, about=,%(about)s WHERE id = %(hr_id)s ;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete_student(cls, data):
        query = "DELETE FROM students WHERE id = %(student_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @staticmethod
    def validate_student(student):
        is_valid = True
        if not EMAIL_REGEX.match(student['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(student['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(student['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        if len(student['password'])< 8:
            flash('Password must be more or equal to 8 characters', 'password')
            is_valid = False
        if 'confirmpassword' in student and student['confirmpassword'] != student['password']:
            flash('The passwords do not match',  'passwordConfirm')
            is_valid = False
        if len(student['about'])< 8:
            flash('About must be more or equal to 8 characters', 'about')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_student_update(student):
        is_valid = True
        if not EMAIL_REGEX.match(student['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(student['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(student['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        if len(student['about'])< 8:
            flash('About must be more or equal to 8 characters', 'about')
            is_valid = False
        return is_valid