import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from firebase_config import firebase_storage
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
        
        if User.get_by_email(email):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user_data = firebase_db.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        if not user_data:
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.get_by_email(email)
        
        if user and firebase_db.verify_password(user.__dict__, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
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
    return render_template('dashboard.html', appointments=appointments)

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
                    
                    # Upload to Firebase Storage
                    attachment_url = firebase_storage.upload_file(
                        file, 
                        unique_filename, 
                        folder='appointments'
                    )
                    attachment_filename = filename
                    flash('File uploaded successfully!', 'success')
                    
                except Exception as e:
                    flash(f'Error uploading file: {str(e)}', 'error')
        
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
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('book_appointment.html')

@app.route('/education')
def education():
    # For now, return empty articles list since we're focusing on appointments
    articles = []
    return render_template('education.html', articles=articles)

@app.route('/about')
def about():
    return render_template('about.html')

# Admin routes
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = firebase_db.get_user_count()
    total_appointments = firebase_db.get_appointment_count()
    pending_appointments = firebase_db.get_pending_appointments_count()
    recent_appointments = firebase_db.get_recent_appointments(5)
    recent_users = firebase_db.get_all_users()[:5]  # Get first 5 users
    
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

@app.route('/admin/appointment/<appointment_id>/update', methods=['POST'])
@login_required
@admin_required
def update_appointment_status(appointment_id):
    status = request.form['status']
    success = firebase_db.update_appointment_status(appointment_id, status)
    if success:
        flash('Appointment status updated', 'success')
    else:
        flash('Failed to update appointment status', 'error')
    return redirect(url_for('admin_appointments'))

def create_admin_user():
    """Create admin user if it doesn't exist"""
    try:
        admin = firebase_db.get_user_by_email('admin@fixandfit.com')
        if not admin:
            admin_data = firebase_db.create_user(
                email='admin@fixandfit.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            if admin_data:
                print("Admin user created: admin@fixandfit.com / admin123")
            else:
                print("Failed to create admin user")
    except Exception as e:
        print(f"Error creating admin user: {e}")

# Initialize admin user on startup
create_admin_user()

if __name__ == '__main__':
    app.run(debug=True)
