from flask import Flask
from config import Config
#from models import User, Service, Availability, db

from flask_mail import Mail, Message

from flask_sqlalchemy import SQLAlchemy  # type: ignore[import]

from flask_mail import Mail, Message

from flask_login import (  # type: ignore[import]
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from models import (
    User,
    Service,
    Availability,
    Appointment,
    db
)










#mail = Mail(app)
app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

def send_email(subject, recipient, body):

    msg = Message(

        subject,

        sender=app.config["MAIL_USERNAME"],

        recipients=[recipient]

    )

    msg.body = body

    mail.send(msg)

@app.route("/")
def home():
    return render_template("register.html")


login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])

def register():

    if request.method == "POST":

        username = request.form["username"].strip().lower()

        name = request.form["name"].strip()

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        role = request.form["role"]


        # CHECK USERNAME
        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:
            flash("Username already exists")
            return redirect(url_for("register"))


        # CHECK EMAIL
        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            flash("Email already exists")
            return redirect(url_for("register"))


        # HASH PASSWORD
        hashed_password = generate_password_hash(password)


        # CREATE USER
        user = User(
            username=username,
            name=name,
            email=email,
            password_hash=hashed_password,
            role=role
        )


        # DOCTOR APPROVAL SYSTEM
        if role == "doctor":
            user.is_verified = False
        else:
            user.is_verified = True


        db.session.add(user)

        db.session.commit()

        flash("Account created successfully")

        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        username = request.form["username"].strip().lower()

        password = request.form["password"]


        user = User.query.filter_by(
            username=username
        ).first()


        # USER EXISTS
        if user:

            # CHECK BLOCKED
            if user.is_blocked:
                flash("Account blocked")
                return redirect(url_for("login"))


            # CHECK PASSWORD
            if check_password_hash(
                user.password_hash,
                password
            ):

                # CHECK DOCTOR APPROVAL
                if user.role == "doctor" and not user.is_verified:
                    flash("Doctor account pending admin approval")
                    return redirect(url_for("login"))


                # LOGIN USER
                login_user(user)

                flash("Login successful")


                # ROLE REDIRECT
                if user.role == "admin":
                    return redirect("/admin/dashboard")

                elif user.role == "doctor":
                    return redirect("/doctor/dashboard")

                else:
                    return redirect("/patient/dashboard")


        flash("Invalid credentials")

    return render_template("login.html")



@app.route("/logout")

@login_required

def logout():

    logout_user()

    flash("Logged out successfully")

    return redirect(url_for("login"))

@app.route("/admin/dashboard")

@login_required

def admin_dashboard():

    if current_user.role != "admin":
        return "Access Denied"

    return render_template(
        "admin_dashboard.html"
    )


@app.route("/doctor/dashboard")

@login_required

def doctor_dashboard():

    if current_user.role != "doctor":
        return "Access Denied"

    return render_template(
        "doctor_dashboard.html"
    )

@app.route("/patient/dashboard")

@login_required

def patient_dashboard():

    if current_user.role != "patient":
        return "Access Denied"

    return render_template(
        "patient_dashboard.html"
    )
    
    
@app.route(
    "/doctor/services/add",
    methods=["GET", "POST"]
)

@login_required

def add_service():

    if current_user.role != "doctor":
        return "Access Denied"


    if request.method == "POST":

        title = request.form["title"]

        description = request.form["description"]

        duration = request.form["duration"]

        fee = request.form["fee"]


        service = Service(

            doctor_id=current_user.id,

            title=title,

            description=description,

            duration=duration,

            fee=fee
        )


        db.session.add(service)

        db.session.commit()

        flash("Service added successfully")

        return redirect(
            url_for("doctor_services")
        )

    return render_template(
        "add_service.html"
    )
    
@app.route("/doctor/services")

@login_required

def doctor_services():

    if current_user.role != "doctor":
        return "Access Denied"


    services = Service.query.filter_by(
        doctor_id=current_user.id
    ).all()


    return render_template(
        "doctor_services.html",
        services=services
    )
    

@app.route("/admin/doctors")

@login_required

def admin_doctors():

    if current_user.role != "admin":
        return "Access Denied"


    doctors = User.query.filter_by(
        role="doctor"
    ).all()


    return render_template(
        "admin_doctors.html",
        doctors=doctors
    )
    
@app.route("/admin/doctors/approve/<int:doctor_id>")

@login_required

def approve_doctor(doctor_id):

    if current_user.role != "admin":
        return "Access Denied"


    doctor = User.query.get_or_404(doctor_id)

    doctor.is_verified = True

    db.session.commit()
    
    
    send_email(

    subject="Doctor Account Approved",

    recipient=doctor.email,

    body=f"""

Hello Dr. {doctor.name},

Your doctor account has been approved.

You can now login to MediSlot.

"""
)
    

    flash("Doctor approved successfully")

    return redirect(
        url_for("admin_doctors")
    )
    
@app.route("/admin/doctors/block/<int:doctor_id>")

@login_required

def block_doctor(doctor_id):

    if current_user.role != "admin":
        return "Access Denied"


    doctor = User.query.get_or_404(doctor_id)

    doctor.is_blocked = True

    db.session.commit()

    flash("Doctor blocked successfully")

    return redirect(
        url_for("admin_doctors")
    )


@app.route(
    "/doctor/availability/add",
    methods=["GET", "POST"]
)

@login_required

def add_availability():

    if current_user.role != "doctor":
        return "Access Denied"


    if request.method == "POST":

        day = request.form["day"]

        start_time = request.form["start_time"]

        end_time = request.form["end_time"]


        availability = Availability(

            doctor_id=current_user.id,

            day=day,

            start_time=start_time,

            end_time=end_time
        )


        db.session.add(availability)

        db.session.commit()

        flash("Availability added successfully")

        return redirect(
            url_for("doctor_availability")
        )


    return render_template(
        "add_availability.html"
    )


@app.route("/doctor/availability")

@login_required

def doctor_availability():

    if current_user.role != "doctor":
        return "Access Denied"


    availabilities = Availability.query.filter_by(
        doctor_id=current_user.id
    ).all()


    return render_template(
        "doctor_availability.html",
        availabilities=availabilities
    )


@app.route("/patient/book")

@login_required

def patient_book():

    if current_user.role != "patient":
        return "Access Denied"


    search = request.args.get("search", "")

    doctors = User.query.filter(

    User.role == "doctor",

    User.is_verified == True,

    User.name.ilike(f"%{search}%")

    ).all()


    return render_template(
        "patient_book.html",
        doctors=doctors
    )
    
    
@app.route(
    "/patient/book/<int:doctor_id>",
    methods=["GET", "POST"]
)

@login_required

def book_appointment(doctor_id):

    if current_user.role != "patient":
        return "Access Denied"


    doctor = User.query.get_or_404(
        doctor_id
    )


    services = Service.query.filter_by(
        doctor_id=doctor.id
    ).all()


    if request.method == "POST":
        service_id = request.form["service_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]

        existing_appointment = Appointment.query.filter_by(

        doctor_id=doctor.id,

        appointment_date=appointment_date,

        appointment_time=appointment_time
        ).first()

        if existing_appointment:
            flash(
                "You already booked an appointment with this doctor on this date"
            )
            return redirect(
                url_for(
                    "book_appointment",
                    doctor_id=doctor.id
                )   
            )

        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            service_id=service_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )

        db.session.add(appointment)
        db.session.commit()

        send_email(
            subject="Appointment Booked",
            recipient=current_user.email,
            body=f"""
Your appointment request has been submitted.
Doctor: Dr. {doctor.name}
Date: {appointment_date}
Status: Pending
Thank you for using MediSlot.
"""
        )

        flash("Appointment booked successfully")
        return redirect(
            url_for("my_appointments")
        )

    return render_template(
        "book_appointment.html",
        doctor=doctor,
        services=services
    )
    
@app.route("/patient/appointments")

@login_required

def my_appointments():

    if current_user.role != "patient":
        return "Access Denied"


    appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).all()


    return render_template(
        "my_appointments.html",
        appointments=appointments
    )


@app.route("/doctor/appointments")

@login_required

def doctor_appointments():

    if current_user.role != "doctor":
        return "Access Denied"


    appointments = Appointment.query.filter_by(
        doctor_id=current_user.id
    ).all()


    return render_template(
        "doctor_appointments.html",
        appointments=appointments
    )
    

@app.route(
    "/doctor/appointment/approve/<int:appointment_id>"
)

@login_required

def approve_appointment(appointment_id):

    if current_user.role != "doctor":
        return "Access Denied"


    appointment = Appointment.query.get_or_404(
        appointment_id
    )


    appointment.status = "Approved"

    db.session.commit()

    patient = User.query.get(
        appointment.patient_id
    )
    '''
    send_email(
        subject="Appointment Approved",
        recipient=patient.email,
        body=f"""
Your appointment has been approved.

Appointment ID:
{appointment.id}
"""
    )
    '''
    flash("Appointment approved")

    return redirect(
        url_for("doctor_appointments")
    )
    
@app.route(
    "/doctor/appointment/reject/<int:appointment_id>"
)

@login_required

def reject_appointment(appointment_id):

    if current_user.role != "doctor":
        return "Access Denied"


    appointment = Appointment.query.get_or_404(
        appointment_id
    )


    appointment.status = "Rejected"

    db.session.commit()

    patient = User.query.get(
        appointment.patient_id
    )
    '''
    send_email(
        subject="Appointment Rejected",
        recipient=patient.email,
        body=f"""
Your appointment request was rejected.

Appointment ID:
{appointment.id}

"""
    )
    '''

    flash("Appointment rejected")

    return redirect(
        url_for("doctor_appointments")
    )

    

@app.route("/test-email")

def test_email():

    send_email(

        subject="MediSlot Test Email",

        recipient="YOUR_GMAIL@gmail.com",

        body="Email system is working successfully."

    )

    return "Test email sent successfully"


@app.route(
    "/patient/appointments/cancel/<int:appointment_id>"
)

@login_required

def cancel_appointment(appointment_id):

    if current_user.role != "patient":
        return "Access Denied"


    appointment = Appointment.query.get_or_404(
        appointment_id
    )


    if appointment.patient_id != current_user.id:
        return "Unauthorized"


    appointment.status = "Cancelled"

    db.session.commit()

    flash("Appointment cancelled")

    return redirect(
        url_for("my_appointments")
    )
    
    
@app.route("/doctor/profile/<int:doctor_id>")

@login_required

def doctor_profile(doctor_id):

    doctor = User.query.get_or_404(
        doctor_id
    )

    services = Service.query.filter_by(
        doctor_id=doctor.id
    ).all()


    return render_template(

        "doctor_profile.html",

        doctor=doctor,

        services=services
    )
    
    


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=False)