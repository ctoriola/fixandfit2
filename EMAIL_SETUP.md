# Email Configuration Guide

This guide explains how to set up the contact form email functionality for Fix and Fit.

## Overview

The contact form now sends emails to `fixfitponigeria@gmail.com` when users submit the form. The system uses Flask-Mail with Gmail's SMTP server.

## Setup Steps

### 1. Enable 2-Factor Authentication on Gmail

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** (left sidebar)
3. Under "How you sign in to Google", enable **2-Step Verification** if not already enabled

### 2. Generate an App-Specific Password

1. Go to **App passwords**: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Windows Computer** (or your platform)
3. Click **Generate**
4. Google will create a 16-character password
5. **Copy this password** - you'll need it for configuration

### 3. Configure Environment Variables

Create a `.env` file in the project root (or update your existing `.env` file) with:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=fixfitponigeria@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=fixfitponigeria@gmail.com
```

Replace `your-16-character-app-password` with the password you generated in Step 2 (remove any spaces).

### 4. Install Dependencies

The required package `Flask-Mail==0.9.1` has been added to `requirements.txt`. Install it:

```bash
pip install -r requirements.txt
```

## How It Works

### Contact Form Flow

1. User fills out the contact form on `/contact`
2. Form submits to `/submit-contact` endpoint via POST
3. Server validates all required fields
4. Email is sent to `fixfitponigeria@gmail.com` with:
   - User's name, email, phone number
   - Subject of inquiry
   - Full message content
   - Reply-to address set to user's email for easy responses

### Email Features

- **Auto-Reply Support**: Emails include `reply_to` field set to user's email, so you can click "Reply" to respond directly to the user
- **Error Handling**: If email fails to send, user is notified with a friendly message
- **Server Logging**: Send errors are logged to console for debugging
- **User Feedback**: Users see success/error messages after form submission

## Testing Email

To test the email functionality locally:

1. Ensure your `.env` file has valid credentials
2. Run the Flask app: `python app.py`
3. Navigate to `/contact`
4. Fill out the form with test data
5. Submit the form
6. Check `fixfitponigeria@gmail.com` for the test email

## Troubleshooting

### Email Not Being Sent

**Problem**: Form submits but no email arrives

**Solutions**:
1. Check that `MAIL_PASSWORD` is correct (16 characters without spaces)
2. Verify 2-Factor Authentication is enabled on the Gmail account
3. Check that the app password was generated correctly from the correct account
4. Look at the Flask console for error messages

### "Less secure app access" Error

**Solution**: This error occurs when Gmail's security blocks the connection. Make sure you're using an **App Password**, not your regular Gmail password. App passwords only work with 2FA enabled.

### Environment Variables Not Loading

**Problem**: Configuration still shows defaults

**Solutions**:
1. Ensure `.env` file is in the project root directory
2. Restart the Flask application after creating/updating `.env`
3. Verify no typos in variable names (case-sensitive: `MAIL_PASSWORD`, not `Mail_Password`)

## Security Notes

- **Never commit `.env` file** to version control - it's already in `.gitignore`
- App passwords are specific to this application only
- If you suspect a compromise, regenerate the app password
- Each Flask deployment can use a different email configuration

## Additional Resources

- [Google Account Help - App Passwords](https://support.google.com/accounts/answer/185833)
- [Flask-Mail Documentation](https://flask-mail.readthedocs.io/)
- [Gmail SMTP Configuration](https://support.google.com/mail/answer/7126229)

## Production Deployment

For production deployment (Vercel, Heroku, etc.):

1. Set environment variables in your platform's dashboard:
   - Vercel: Environment Variables section in Project Settings
   - Heroku: Heroku Vars in Settings
   - AWS: Environment variables in Lambda/Elastic Beanstalk

2. Use the same variable names as in `.env`

3. Never paste the `.env` file directly - always use the platform's configuration interface

## Alternative Email Providers

If you want to use a different email service (SendGrid, AWS SES, etc.), update:

1. `MAIL_SERVER` - SMTP endpoint
2. `MAIL_PORT` - SMTP port (usually 587 or 465)
3. `MAIL_USERNAME` - API key or username
4. `MAIL_PASSWORD` - API key or password
5. `MAIL_USE_TLS` - True for port 587, False for port 465

Consult the email provider's documentation for specific values.
