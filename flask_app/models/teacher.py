from flask_app.config.mysqlconnection import connectToMySQL
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash

class Teacher:
    db_name="projectsdb"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.is_verified = data['is_verified']
        self.verification_code = data['verification_code']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def get_teacher_by_email(cls, data):
        query = 'SELECT * FROM teachers WHERE email= %(email)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    @classmethod
    def get_teacher_by_id(cls, data):
        query = 'SELECT * FROM teachers WHERE id= %(teacher_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False

    @classmethod
    def create_teacher(cls, data):
        query = "INSERT INTO teachers (first_name, last_name, email,  password, verification_code) VALUES ( %(first_name)s, %(last_name)s,%(email)s,%(password)s, %(verification_code)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update_teacher(cls, data):
        query = "UPDATE teachers SET first_name = %(first_name)s, last_name = %(last_name)s, email= %(email)s WHERE id = %(teacher_id)s ;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def updateVerificationCode(cls, data):
        query = "UPDATE teachers SET verification_code = %(verification_code)s WHERE teacher.id = %(teacher_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def activateAccount(cls, data):
        query = "UPDATE teacher set is_verified = 1 WHERE teachers.id = %(teacher_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def delete_teacher(cls, data):
        query = "DELETE FROM teachers WHERE id = %(teacher_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @staticmethod
    def validate_teacher(teacher):
        is_valid = True
        if not EMAIL_REGEX.match(teacher['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(teacher['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(teacher['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        if len(teacher['password'])< 8:
            flash('Password must be more or equal to 8 characters', 'password')
            is_valid = False
        if 'confirmpassword' in teacher and teacher['confirmpassword'] != teacher['password']:
            flash('The passwords do not match',  'passwordConfirm')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_teacher_update(teacher):
        is_valid = True
        if not EMAIL_REGEX.match(teacher['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(teacher['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(teacher['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        return is_valid