from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    record = db.Column(db.Integer)


def getrecord():
    query = Record.query.order_by(Record.record.desc()).first()
    highestRecord = query.record
    return highestRecord


def create(data):
    createRecord = Record(**data)
    db.session.add(createRecord)
    db.session.commit()
    return from_sql(createRecord)


def update(data, record):
    new_record = Record.query.get(record)
    for k, v in new_record.items():
      setattr(new_record, k, v)
    db.session.commit()
    return from_sql(new_record)


def create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('appengine_config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")

