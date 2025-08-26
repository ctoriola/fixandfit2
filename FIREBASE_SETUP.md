# Firebase Storage Setup Guide

This guide will help you set up Firebase Storage for file uploads in your Fix and Fit Flask application.

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter project name (e.g., "fixandfit-healthcare")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Firebase Storage

1. In your Firebase project console, click "Storage" in the left sidebar
2. Click "Get started"
3. Choose "Start in test mode" for now (we'll secure it later)
4. Select a storage location (choose closest to your users)
5. Click "Done"

## Step 3: Create Service Account

1. Go to Project Settings (gear icon) → "Service accounts"
2. Click "Generate new private key"
3. Download the JSON file (keep it secure!)
4. Note your project ID and storage bucket name

## Step 4: Configure Environment Variables

### Option A: Using JSON Config (Recommended for Vercel)

1. Open the downloaded service account JSON file
2. Copy the entire JSON content
3. In your deployment platform (Vercel), set these environment variables:
   - `FIREBASE_CONFIG`: Paste the entire JSON as a single line
   - `FIREBASE_STORAGE_BUCKET`: your-project-id.appspot.com

### Option B: Using Service Account File (Local Development)

1. Place the JSON file in your project root as `firebase-service-account.json`
2. Add to `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json
   FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   ```

## Step 5: Security Rules (Production)

Replace the default Storage rules with:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /appointments/{allPaths=**} {
      allow read, write: if request.auth != null;
    }
    match /{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## Step 6: Test the Integration

1. Install dependencies: `pip install -r requirements.txt`
2. Set up your environment variables
3. Run the Flask app: `python app.py`
4. Try booking an appointment with a file attachment

## Supported File Types

- **Documents**: PDF, DOC, DOCX
- **Images**: PNG, JPG, JPEG, GIF
- **Size limit**: 10MB per file

## Troubleshooting

### Common Issues:

1. **"Firebase not initialized"**
   - Check environment variables are set correctly
   - Verify JSON format in FIREBASE_CONFIG

2. **"Permission denied"**
   - Update Storage security rules
   - Check service account permissions

3. **"File upload failed"**
   - Verify file type is allowed
   - Check file size (max 10MB)
   - Ensure Firebase Storage is enabled

### Environment Variables Checklist:

- ✅ `FIREBASE_CONFIG` or `GOOGLE_APPLICATION_CREDENTIALS`
- ✅ `FIREBASE_STORAGE_BUCKET`
- ✅ `SECRET_KEY`
- ✅ `DATABASE_URL`

## Production Deployment

For Vercel deployment:

1. Set environment variables in Vercel dashboard
2. Use `FIREBASE_CONFIG` with JSON string (not file path)
3. Ensure all Firebase services are properly configured
4. Test file uploads after deployment

## File Organization

Files are uploaded to Firebase Storage with this structure:
```
/appointments/
  ├── uuid1_document.pdf
  ├── uuid2_xray.jpg
  └── uuid3_prescription.pdf
```

Each file gets a unique UUID prefix to prevent naming conflicts.
