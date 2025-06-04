from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    request_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def can_make_request(self, limit):
        return self.request_count < limit

    def increment_request_count(self):
        self.request_count += 1
        db.session.commit()

class BotMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text)
    response_text = db.Column(db.Text)
    response_time_ms = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BotStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_requests = db.Column(db.Integer, default=0)

    @staticmethod
    def get_current_stats():
        stats = BotStats.query.first()
        if not stats:
            stats = BotStats(total_requests=0)
            db.session.add(stats)
            db.session.commit()
        return stats

    def update_stats(self):
        self.total_requests += 1
        db.session.commit()