from flask_sqlalchemy import SQLAlchemy

from .validators import validate_user
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def setup_db(app, mode: str = None):
    """
    setup_db(app)
        binds a flask application and a SQLAlchemy service
    """
    with app.app_context():
        if mode is None:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opendata.db'
        app.config['SQLALCHEMY_NOTIFICATIONS'] = False
        db.app = app
        db.init_app(app)


def db_drop_and_create_all(app):
    """
    db_drop_and_create_all()
        drops the database tables and starts fresh
        can be used to initialize a clean database
        !!NOTE you can change the database_filename variable to have multiple versions of a database
    """
    with app.app_context():
        db.drop_all()
        db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String())
    password_hash = db.Column(db.String(), nullable=False)
    occupation = db.Column(db.String(120))
    place_of_work = db.Column(db.String(120))
    purpose = db.Column(db.String(120))

    def create(self, first_name, last_name, email, password, occupation, place_of_work, purpose):
        """Create New User"""

        if not validate_user(first_name=first_name, email=email, password=password):
            raise AuthError("Invalid Credentials")

        existing_user = User.get_by_email(email)
        if existing_user:
            raise AuthError("Email already registered")

        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = generate_password_hash(password=password)
        self.occupation = occupation
        self.place_of_work = place_of_work
        self.purpose = purpose

        db.session.add(self)
        db.session.commit()
        return True

    @staticmethod
    def get_by_id(user_id):
        return db.session.execute(db.select([User]).where(User.id == user_id)).fetchone()[0]

    @staticmethod
    def get_by_email(email):
        return db.session.execute(db.select([User]).where(User.email == email)).fetchone()[0]

    def check_password(self, password):
        if not check_password_hash(self.password_hash, password):
            raise AuthError("Invalid Credentials")


class AuthError(Exception):
    def __init__(self, message="Authentication error occurred."):
        self.message = message
        super().__init__(self.message)