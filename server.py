from flask_app import app

# import our controllers
from flask_app.controllers import students, projects,env,teachers,events

if __name__=="__main__":   # Ensure this file is being run directly and not from a different module    
    app.run(debug=True)   