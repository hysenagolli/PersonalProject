from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash  

class Project:
    db_name = 'projectsdb'
    def __init__(self , data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.job_post_image = data['job_post_image']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.star_rating= data['star_rating']
        
    @classmethod
    def update(cls, data):
        query = "UPDATE projects set description = %(description)s, tilte=%(title)s WHERE projects.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)   
        
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM projects WHERE id = %(project_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def count_projects(cls):
        query = 'SELECT COUNT(*) FROM projects;'
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']
    
    
    @classmethod
    def get_project_by_id(cls, data):
        query = 'SELECT * FROM projects WHERE id= %(project_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    @classmethod
    def get_all_projects(cls):
        query = 'SELECT * FROM projects;'
        results = connectToMySQL(cls.db_name).query_db(query)
        projects = []
        if results:
            for project in results:
                project = Job(project)
                projects.append(project)
            return projects
        return projects
    @classmethod
    def update_star_rating(cls, project_id, rating):
        query = "UPDATE projects SET star_rating = %(rating)s WHERE id = %(project_id)s;"
        data = {
            'project_id': project_id,
            'rating': rating
        }
        connectToMySQL(cls.db_name).query_db(query, data) 
    @classmethod
    def delete_all_project_ratings(cls, data):
        query ="DELETE FROM ratings where ratings.project_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    @classmethod
    def search(cls, search_query):

        query = f"""
            SELECT * FROM projects where projects.title LIKE '{search_query}%'
        """

        try:
            results = connectToMySQL(cls.db_name).query_db(query)

            projects = []
            if results:
                for project in results:
                    projects.append(project)
            return projects
        except Exception as e:
            print("An error occurred:", str(e))
            return []
    @classmethod
    def createPayment(cls,data):
        query = "INSERT INTO payments (ammount, status, project_id) VALUES (%(ammount)s, %(status)s, %(project_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_allUserPayments(cls, data):
        query = "SELECT * FROM payments where teacher_id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        payments = []
        if results:
            for pay in results:
                payments.append(pay)
        return payments    
    
    @classmethod
    def get_student_project_by_id(cls, data):
        query = 'SELECT * FROM projects WHERE student_id= %(student_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        return results 
    
    @classmethod
    def get_job_creator(cls, data):
        query="SELECT jobs.id AS job_id, jobs.provider_id, providers.id AS provider_id, provider.first_name as first_name, providers.last_name as last_name, profession,email FROM jobs LEFT JOIN providers ON jobs.provider_id = providers.id WHERE jobs.id= %(job_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def create_project(cls, data):
        query = "INSERT INTO projects (title, descriptione, job_post_image,  student_id) VALUES ( %(title)s, %(description)s, %(job_post_image)s, %(student_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @staticmethod
    def validateImage(data):
        is_valid = True
        if len(data) < 1:
            flash('Please select at least one image', 'job_post_image')
            is_valid = False 
        return is_valid
    
    @staticmethod
    def validateImageLogo(data):
        is_valid = True
        if len(data) < 1:
            flash('Please select at least one image', 'company_logo')
            is_valid = False 
        return is_valid
    
    @staticmethod
    def validate_project(student):
        is_valid = True
        if len(student['title'])< 3:
            flash('Title must be more than 2 characters', 'title')
            is_valid = False
        if len(student['description'])< 3:
            flash('Description must be more than 2 characters', 'description')
            is_valid = False
        return is_valid
    