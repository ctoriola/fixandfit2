import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from aws_storage import cloudinary_storage
from firebase_db import firebase_db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login compatibility
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        self.phone = user_data.get('phone')
        self.patient_card_number = user_data.get('patient_card_number')
        self.date_of_birth = user_data.get('date_of_birth')
        self.address = user_data.get('address')
        self.emergency_contact = user_data.get('emergency_contact')
        self.emergency_phone = user_data.get('emergency_phone')
        self.is_admin = user_data.get('is_admin', False)
        self.created_at = user_data.get('created_at')
        self.password_hash = user_data['password_hash']
    
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get(user_id):
        user_data = firebase_db.get_user_by_id(user_id)
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_email(email):
        user_data = firebase_db.get_user_by_email(email)
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_patient_number(patient_number):
        user_data = firebase_db.get_user_by_patient_number(patient_number)
        if user_data:
            return User(user_data)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        date_of_birth = request.form.get('date_of_birth')
        address = request.form.get('address')
        emergency_contact = request.form.get('emergency_contact')
        emergency_phone = request.form.get('emergency_phone')
        patient_card_number = request.form.get('patient_card_number')
        
        if User.get_by_email(email):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user_data = firebase_db.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            patient_card_number=patient_card_number,
            date_of_birth=date_of_birth,
            address=address,
            emergency_contact=emergency_contact,
            emergency_phone=emergency_phone,
            is_admin=False
        )
        
        if not user_data:
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
        
        flash(f'Registration successful! Your patient number is: {user_data.get("patient_card_number", "N/A")}. Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['email']  # Can be email or patient number
        password = request.form['password']
        
        try:
            print(f"Login attempt with input: {login_input}")
            
            # Try to get user by email first, then by patient number
            user = User.get_by_email(login_input)
            if not user:
                print(f"User not found by email, trying patient number")
                user = User.get_by_patient_number(login_input)
            
            if user:
                print(f"User found: {user.email}, verifying password")
                if firebase_db.verify_password(user.__dict__, password):
                    print(f"Password verified, logging in user")
                    login_user(user)
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    elif user.is_admin:
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('dashboard'))
                else:
                    print(f"Password verification failed")
                    flash('Invalid email/patient number or password', 'error')
            else:
                print(f"User not found")
                flash('Invalid email/patient number or password', 'error')
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    appointments = firebase_db.get_appointments_by_user(current_user.id)
    appointments.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    recent_appointments = appointments[:5]  # Get 5 most recent
    
    patient_history = firebase_db.get_patient_history(current_user.id)
    
    return render_template('dashboard.html', appointments=recent_appointments, patient_history=patient_history)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        service_type = request.form['service_type']
        appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%dT%H:%M')
        notes = request.form.get('notes', '')
        
        # Handle file upload
        attachment_url = None
        attachment_filename = None
        
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '' and allowed_file(file.filename):
                try:
                    # Generate unique filename
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    
                    # Upload to Cloudinary
                    attachment_url = cloudinary_storage.upload_file(
                        file, 
                        unique_filename, 
                        folder='appointments'
                    )
                    attachment_filename = filename
                    flash('File uploaded successfully!', 'success')
                    
                except Exception as e:
                    flash(f'Error uploading file: {str(e)}', 'error')
        
        print(f"Booking appointment for user ID: {current_user.id}")
        print(f"Service: {service_type}, Date: {appointment_date.date()}, Time: {appointment_date.time()}")
        
        appointment = firebase_db.create_appointment(
            user_id=current_user.id,
            service=service_type,
            date=appointment_date.date(),
            time=appointment_date.time(),
            notes=notes,
            attachment_url=attachment_url,
            attachment_filename=attachment_filename
        )
        
        if not appointment:
            flash('Failed to book appointment. Please try again.', 'error')
            return render_template('book_appointment.html')
        
        print(f"Appointment created successfully: {appointment}")
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('book_appointment.html')

@app.route('/education')
def education():
    # For now, return empty articles list since we're focusing on appointments
    articles = []
    return render_template('education.html', articles=articles)

# Admin routes
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    print("Admin Dashboard: Loading data...")
    total_users = firebase_db.get_user_count()
    total_appointments = firebase_db.get_appointment_count()
    pending_appointments = firebase_db.get_pending_appointments_count()
    recent_appointments = firebase_db.get_recent_appointments(5)
    recent_users = firebase_db.get_all_users()[:5]  # Get first 5 users
    
    print(f"Admin Dashboard: Stats - Users: {total_users}, Appointments: {total_appointments}, Pending: {pending_appointments}")
    print(f"Admin Dashboard: Recent appointments count: {len(recent_appointments)}")
    print(f"Admin Dashboard: Recent users count: {len(recent_users)}")
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         recent_appointments=recent_appointments,
                         recent_users=recent_users)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = firebase_db.get_all_users()
    return render_template('admin/users.html', users=users)

@app.route('/admin/appointments')
@login_required
@admin_required
def admin_appointments():
    appointments = firebase_db.get_all_appointments()
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    return render_template('admin/settings.html')

@app.route('/admin/update_appointment_status/<appointment_id>/<status>')
@login_required
def update_appointment_status(appointment_id, status):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    success = firebase_db.update_appointment_status(appointment_id, status)
    if success:
        flash('Appointment status updated', 'success')
    else:
        flash('Failed to update appointment status', 'error')
    return redirect(url_for('admin_appointments'))

@app.route('/admin/user/<user_id>')
@login_required
def admin_view_user(user_id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    user = firebase_db.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin_users'))
    
    # Get patient history
    patient_history = firebase_db.get_patient_history(user_id)
    
    return render_template('admin/view_user.html', user=user, patient_history=patient_history)

@app.route('/admin/add_diagnosis/<user_id>', methods=['GET', 'POST'])
@login_required
def add_diagnosis(user_id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    user = firebase_db.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        notes = request.form.get('notes')
        
        if not diagnosis or not treatment:
            flash('Diagnosis and treatment are required', 'error')
            return render_template('admin/add_diagnosis.html', user=user)
        
        diagnosis_data = firebase_db.create_diagnosis(
            user_id=user_id,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes,
            created_by_admin=current_user.id
        )
        
        if diagnosis_data:
            flash('Diagnosis added successfully', 'success')
            return redirect(url_for('admin_view_user', user_id=user_id))
        else:
            flash('Failed to add diagnosis', 'error')
    
    return render_template('admin/add_diagnosis.html', user=user)

@app.route('/admin/update_diagnosis_status/<diagnosis_id>/<status>', methods=['POST'])
@login_required
def update_diagnosis_status(diagnosis_id, status):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    success = firebase_db.update_diagnosis_status(diagnosis_id, status)
    if success:
        flash('Diagnosis status updated', 'success')
    else:
        flash('Failed to update diagnosis status', 'error')
    
    return '', 200

def create_admin_user():
    """Create admin user if it doesn't exist"""
    try:
        # Force delete existing admin if any
        admin = firebase_db.get_user_by_email('admin@fixandfit.com')
        if admin:
            print("Deleting existing admin user")
            firebase_db.db.collection('users').document(admin['id']).delete()
        
        # Create fresh admin user
        admin_data = firebase_db.create_user(
            email='admin@fixandfit.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            phone='+1234567890',
            is_admin=True
        )
        if admin_data:
            print("NEW Admin user created: admin@fixandfit.com / admin123")
        else:
            print("Failed to create admin user")
    except Exception as e:
        print(f"Error creating admin user: {e}")

# Create admin user on startup if none exists
create_admin_user()

if __name__ == '__main__':
    app.run(debug=True)
