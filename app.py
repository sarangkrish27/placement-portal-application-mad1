from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'danger'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    from routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        from models import User, update_drive_status
        
        db.create_all()
        update_drive_status()

        admin = User.query.filter_by(role='admin').first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash('admin123')
            admin = User(
                email='admin@placement.nist.edu',
                password=hashed_password,
                role='admin',
                is_profile_completed=True
            )
            db.session.add(admin)
            db.session.commit()

    return app