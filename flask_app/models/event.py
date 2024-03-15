from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
class Event:
    db_name = "projectsdb"
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.event_images = data['event_images']
        self.deadline = data['deadline']
        self.teacher_id = data['teacher_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    
    @classmethod
    def create(cls, data):
        query = "INSERT INTO events (title, description,event_images,deadline, teacher_id) VALUES (%(title)s, %(description)s, %(event_images)s,%(deadline)s, %(teacher_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
     
    @staticmethod
    def validateImage(data):
        is_valid = True
        if len(data) < 1:
            flash('Please select at least one image', 'event_images')
            is_valid = False 
        return is_valid
    
    @classmethod
    def get_all_event(cls):
        query = "SELECT * FROM events;"
        results = connectToMySQL(cls.db_name).query_db(query)
        events = []
        if results:
            for event in results:
                events.append(event)
        return events
    
    @classmethod
    def update_profile_pic_student(cls, data):
        query = "UPDATE events SET event_images = %(image)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)    

    @classmethod
    def count_likes(cls):
        query = 'SELECT COUNT(*) FROM likes;'
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']

    @classmethod
    def get_event_by_id(cls, data):
        query = "SELECT * FROM events LEFT JOIN students  on events.student_id = students.id WHERE events.id = %(id)s;"
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            comments = []
            query2 = "SELECT * FROM comments left join students on comments.student_id = students.id where comments.event_id = %(id)s;"
            result2 = connectToMySQL(cls.db_name).query_db(query2, data)
            if result2:
                for comment in result2:
                    comments.append(comment)
            result[0]['comments'] = comments
            query3 = "SELECT students.first_name, students.last_name FROM likes left join students on likes.student_id = students.id where likes.event_id = %(id)s;"
            result3 = connectToMySQL(cls.db_name).query_db(query3, data)
            likes = []
            if result3:
                for like in result3:
                    likes.append(like)
            result[0]['likes'] = likes
            return result[0]
        return False
      
    @classmethod
    def get_all_comments(cls):
        query = "SELECT * FROM comments;"
        results = connectToMySQL(cls.db_name).query_db(query)
        comments = []
        if results:
            for comment in results:
                comments.append(comment)
        return comments
    
    @classmethod
    def get_event_by_idd(cls, data):
        query = 'SELECT * FROM events WHERE id= %(id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
  
    @classmethod
    def get_comment_by_id(cls, data):
        query = "SELECT * FROM comments where comments.id = %(id)s;"
        results =  connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM events where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete_all_event_comments(cls, data):
        query ="DELETE FROM comments where comments.event_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update(cls, data):
        query = "UPDATE events set description = %(description)s, title=%(title)s, deadline = %(deadline)s WHERE events.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    
    # functionality for comments
    @classmethod
    def addComment(cls, data):
        query = "INSERT INTO comments (comment, student_id, event_id) VALUES (%(comment)s, %(student_id)s, %(event_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    @classmethod
    def update_comment(cls, data):
        query = "UPDATE comments set comment = %(comment)s where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete_comment(cls, data):
        query = "DELETE FROM comments where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
      

    @classmethod
    def addLike(cls, data):
        query = "INSERT INTO likes (student_id, event_id) VALUES (%(student_id)s, %(event_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def removeLike(cls, data):
        query = "DELETE FROM likes WHERE event_id=%(event_id)s AND student_id = %(student_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_students_who_liked_by_event_id(cls, data):
        query ="SELECT student_id FROM likes where event_id = %(event_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        studentsId = []
        if results:
            for studentId in results:
                studentsId.append(studentId['student_id'])
        return studentsId
                

    @staticmethod
    def validate_event(event):
        is_valid = True
        if len(event['title'])< 2:
            flash('Title should be more  or equal to 2 characters', 'title')
            is_valid = False
        if len(event['description'])< 10:
            flash('Description should be more  or equal to 10 characters', 'description')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_eventUpdate(event):
        is_valid = True
        if len(event['description'])< 10:
            flash('Description should be more  or equal to 10 characters', 'description')
            is_valid = False
        if len(event['title'])< 2:
            flash('Title should be more  or equal to 2 characters', 'title')
            is_valid = False
        return is_valid