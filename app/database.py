from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from app.models import AllUsers

db = SQLAlchemy()

def create_tables():
    # Check if the AllUsers table exists, if not, create it
    with db.app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table(AllUsers.__tablename__):
            db.create_all()
