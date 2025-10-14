import os
from main import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from main import db
        db.create_all()
    
    port = os.getenv('PORT', 7000) 
    app.run(debug=True, port=port)


    