from datetime import datetime
from . import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    request_count = db.Column(db.Integer, default=0)
    last_request_time = db.Column(db.DateTime)

    generations = db.relationship('Generation', backref='user', lazy=True)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

class Generation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    niche = db.Column(db.String(100))
    content_type = db.Column(db.String(100))
    engine = db.Column(db.String(50))
    language = db.Column(db.String(10))
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)