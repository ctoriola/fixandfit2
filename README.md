# Fix and Fit - Healthcare Management System

A modern Flask-based web application for managing prosthetics, orthotics, and pedorthotics appointments and services.

## Features

- **User Authentication** - Secure login/registration system
- **Appointment Booking** - Online appointment scheduling
- **Admin Dashboard** - Complete management interface
- **Modern UI** - Clean SaaS-style design with DM Sans typography
- **Responsive Design** - Works on desktop and mobile devices

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Werkzeug password hashing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ctoriola/fixandfit2.git
cd fixandfit2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
python app.py
```

5. Access the application at `http://localhost:5000`

## Deployment

### Vercel Deployment

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `SECRET_KEY`: Your Flask secret key
   - `DATABASE_URL`: PostgreSQL connection string (recommended for production)
3. Deploy automatically on push to main branch

### Environment Variables

- `SECRET_KEY`: Flask session security key
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Set to `production` for deployment

## Default Admin Account

- **Email**: admin@fixandfit.com
- **Password**: admin123

## Services

- Prosthetics Consultation
- Orthotics Consultation  
- pedorthotics Consultation
- Fitting Appointments
- Follow-up Visits
- Repair Services

## Project Structure

```
flask-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── admin/            # Admin templates
│   └── ...
└── instance/             # SQLite database (auto-created)
```

## License

MIT License
