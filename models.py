from flask_sqlalchemy import SQLAlchemy  # type: ignore[import]
from flask_login import UserMixin  # type: ignore[import]

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )

    is_blocked = db.Column(
        db.Boolean,
        default=False
    )
    
    
class Service(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    title = db.Column(
        db.String(120),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    fee = db.Column(
        db.Integer,
        nullable=False
    )
    
    
class Availability(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    day = db.Column(
        db.String(20),
        nullable=False
    )

    start_time = db.Column(
        db.String(20),
        nullable=False
    )

    end_time = db.Column(
        db.String(20),
        nullable=False
    )
    
class Appointment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey('service.id'),
        nullable=False
    )

    appointment_date = db.Column(
        db.String(30),
        nullable=False
    )
    
    appointment_time = db.Column(
    db.String(20),
    nullable=False
    )
    
    status = db.Column(
    db.String(50),
    default="Pending"
    )