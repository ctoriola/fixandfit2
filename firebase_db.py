import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash, check_password_hash

class FirebaseDB:
    def __init__(self):
        self.db = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK for Firestore"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get Firebase config from environment variable
                firebase_config = os.environ.get('FIREBASE_CONFIG')
                
                if firebase_config:
                    # Parse JSON config from environment variable
                    config_dict = json.loads(firebase_config)
                    cred = credentials.Certificate(config_dict)
                else:
                    # Fallback to service account file
                    service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'firebase-service-account.json')
                    if os.path.exists(service_account_path):
                        cred = credentials.Certificate(service_account_path)
                    else:
                        print("Warning: Firebase credentials not found. Database will not work.")
                        return
                
                # Initialize Firebase app
                firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            self.db = firestore.client()
            print("Firebase Firestore initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Firebase Firestore: {e}")
            self.db = None
    
    # User Management
    def create_user(self, email, password, first_name, last_name, phone=None, is_admin=False):
        """Create a new user"""
        if not self.db:
            raise Exception("Firestore not initialized")
        
        try:
            user_data = {
                'email': email,
                'password_hash': generate_password_hash(password),
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'is_admin': is_admin,
                'created_at': datetime.utcnow()
            }
            
            # Check if user already exists
            existing_user = self.db.collection('users').where('email', '==', email).limit(1).get()
            if existing_user:
                return None  # User already exists
            
            # Create user document
            doc_ref = self.db.collection('users').add(user_data)
            user_data['id'] = doc_ref[1].id
            return user_data
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        if not self.db:
            return None
        
        try:
            users = self.db.collection('users').where('email', '==', email).limit(1).get()
            if users:
                user_doc = users[0]
                user_data = user_doc.to_dict()
                user_data['id'] = user_doc.id
                return user_data
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        if not self.db:
            return None
        
        try:
            user_doc = self.db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['id'] = user_doc.id
                return user_data
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def get_all_users(self):
        """Get all users"""
        if not self.db:
            return []
        
        try:
            users = []
            docs = self.db.collection('users').order_by('created_at', direction=firestore.Query.DESCENDING).get()
            for doc in docs:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                users.append(user_data)
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def verify_password(self, user_data, password):
        """Verify user password"""
        return check_password_hash(user_data['password_hash'], password)
    
    # Appointment Management
    def create_appointment(self, user_id, service, date, time, notes=None, attachment_url=None, attachment_filename=None):
        """Create a new appointment"""
        if not self.db:
            raise Exception("Firestore not initialized")
        
        try:
            appointment_data = {
                'user_id': user_id,
                'service': service,
                'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                'time': time.isoformat() if hasattr(time, 'isoformat') else str(time),
                'notes': notes,
                'status': 'pending',
                'attachment_url': attachment_url,
                'attachment_filename': attachment_filename,
                'created_at': datetime.utcnow()
            }
            
            doc_ref = self.db.collection('appointments').add(appointment_data)
            appointment_data['id'] = doc_ref[1].id
            return appointment_data
            
        except Exception as e:
            print(f"Error creating appointment: {e}")
            return None
    
    def get_appointments_by_user(self, user_id):
        """Get appointments for a specific user"""
        if not self.db:
            return []
        
        try:
            appointments = []
            docs = self.db.collection('appointments').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).get()
            for doc in docs:
                appointment_data = doc.to_dict()
                appointment_data['id'] = doc.id
                appointments.append(appointment_data)
            return appointments
        except Exception as e:
            print(f"Error getting user appointments: {e}")
            return []
    
    def get_all_appointments(self):
        """Get all appointments"""
        if not self.db:
            return []
        
        try:
            appointments = []
            docs = self.db.collection('appointments').order_by('created_at', direction=firestore.Query.DESCENDING).get()
            for doc in docs:
                appointment_data = doc.to_dict()
                appointment_data['id'] = doc.id
                # Get user data for this appointment
                user_data = self.get_user_by_id(appointment_data['user_id'])
                appointment_data['user'] = user_data
                appointments.append(appointment_data)
            return appointments
        except Exception as e:
            print(f"Error getting all appointments: {e}")
            return []
    
    def get_appointment_by_id(self, appointment_id):
        """Get appointment by ID"""
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('appointments').document(appointment_id).get()
            if doc.exists:
                appointment_data = doc.to_dict()
                appointment_data['id'] = doc.id
                # Get user data for this appointment
                user_data = self.get_user_by_id(appointment_data['user_id'])
                appointment_data['user'] = user_data
                return appointment_data
            return None
        except Exception as e:
            print(f"Error getting appointment by ID: {e}")
            return None
    
    def update_appointment_status(self, appointment_id, status):
        """Update appointment status"""
        if not self.db:
            return False
        
        try:
            self.db.collection('appointments').document(appointment_id).update({
                'status': status,
                'updated_at': datetime.utcnow()
            })
            return True
        except Exception as e:
            print(f"Error updating appointment status: {e}")
            return False
    
    def get_recent_appointments(self, limit=5):
        """Get recent appointments"""
        if not self.db:
            return []
        
        try:
            appointments = []
            docs = self.db.collection('appointments').order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).get()
            for doc in docs:
                appointment_data = doc.to_dict()
                appointment_data['id'] = doc.id
                # Get user data for this appointment
                user_data = self.get_user_by_id(appointment_data['user_id'])
                appointment_data['user'] = user_data
                appointments.append(appointment_data)
            return appointments
        except Exception as e:
            print(f"Error getting recent appointments: {e}")
            return []
    
    # Statistics
    def get_user_count(self):
        """Get total user count"""
        if not self.db:
            return 0
        
        try:
            users = self.db.collection('users').get()
            return len(users)
        except Exception as e:
            print(f"Error getting user count: {e}")
            return 0
    
    def get_appointment_count(self):
        """Get total appointment count"""
        if not self.db:
            return 0
        
        try:
            appointments = self.db.collection('appointments').get()
            return len(appointments)
        except Exception as e:
            print(f"Error getting appointment count: {e}")
            return 0
    
    def get_pending_appointments_count(self):
        """Get pending appointments count"""
        if not self.db:
            return 0
        
        try:
            appointments = self.db.collection('appointments').where('status', '==', 'pending').get()
            return len(appointments)
        except Exception as e:
            print(f"Error getting pending appointments count: {e}")
            return 0

# Global instance
firebase_db = FirebaseDB()
