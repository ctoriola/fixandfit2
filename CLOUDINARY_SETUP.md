# Cloudinary Setup Guide for Fix and Fit

This guide will help you set up Cloudinary for file storage in your Fix and Fit application.

## Prerequisites

- Cloudinary Account (create at https://cloudinary.com if you don't have one)
- Basic understanding of cloud storage services

## Step 1: Create Cloudinary Account

1. **Sign Up**
   - Go to https://cloudinary.com
   - Click "Sign up for free"
   - Complete registration with email or social login

2. **Verify Account**
   - Check your email for verification link
   - Complete account verification

## Step 2: Get Your Credentials

1. **Access Dashboard**
   - Log in to your Cloudinary account
   - You'll see your dashboard with account details

2. **Copy Credentials**
   - On the dashboard, you'll see:
     - **Cloud Name**: Your unique cloud identifier
     - **API Key**: Your public API key
     - **API Secret**: Your private API secret (click "Reveal" to see it)

3. **Example Credentials Format**
   ```
   Cloud Name: your-cloud-name
   API Key: 123456789012345
   API Secret: abcdefghijklmnopqrstuvwxyz123456
   ```

## Step 3: Configure Environment Variables

### For Local Development:
Create a `.env` file in your flask-app directory:
```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### For Vercel Deployment:
1. Go to your Vercel project dashboard
2. Click **"Settings"** → **"Environment Variables"**
3. Add these variables:

**CLOUDINARY_CLOUD_NAME:**
- Name: `CLOUDINARY_CLOUD_NAME`
- Value: Your cloud name (e.g., `dxyz123abc`)

**CLOUDINARY_API_KEY:**
- Name: `CLOUDINARY_API_KEY`
- Value: Your API key (e.g., `123456789012345`)

**CLOUDINARY_API_SECRET:**
- Name: `CLOUDINARY_API_SECRET`
- Value: Your API secret (e.g., `abcdefghijklmnopqrstuvwxyz123456`)

## Step 4: Test the Integration

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Local Test**
   - Start your Flask app locally
   - Try uploading a file through the appointment booking form
   - Check if the file appears in your Cloudinary Media Library

3. **Verify in Cloudinary Dashboard**
   - Go to Media Library in your Cloudinary dashboard
   - You should see uploaded files in the `appointments/` folder

## Features Included

### Automatic Optimizations
- **Image Compression**: Automatically optimizes image file sizes
- **Format Conversion**: Converts to modern formats (WebP, AVIF) when supported
- **Responsive Images**: Can generate different sizes on-the-fly

### File Management
- **Organized Storage**: Files stored in folders (e.g., `appointments/`)
- **Unique Filenames**: Prevents conflicts with UUID-based naming
- **Auto-Detection**: Handles images, videos, and documents automatically

### Security Features
- **Secure URLs**: All files served over HTTPS
- **Access Control**: API keys control upload permissions
- **Signed URLs**: Can generate time-limited access URLs if needed

## Pricing Information

### Free Tier Includes:
- **25 GB** storage
- **25 GB** monthly bandwidth
- **1,000** transformations per month
- **1,000** video seconds per month

### Usage Monitoring:
- Monitor usage in your Cloudinary dashboard
- Set up usage alerts to avoid overages
- Upgrade plan if you exceed free tier limits

## Advanced Features (Optional)

### Image Transformations
The integration includes an `get_optimized_url()` method for:
- **Resizing**: `width=300, height=200`
- **Quality Control**: `quality="auto"` or specific values
- **Format Optimization**: Automatic format selection

### Example Usage:
```python
# Get optimized thumbnail
thumbnail_url = cloudinary_storage.get_optimized_url(
    original_url, 
    width=150, 
    height=150, 
    quality="auto"
)
```

## Troubleshooting

### Common Issues:

1. **Upload Failures**
   - Verify all three environment variables are set correctly
   - Check your Cloudinary dashboard for API key status
   - Ensure your account is verified

2. **File Not Appearing**
   - Check Media Library in Cloudinary dashboard
   - Verify folder structure (should be in `appointments/`)
   - Check for error messages in Flask logs

3. **Access Denied Errors**
   - Verify API Secret is correct (it's case-sensitive)
   - Check if your account has upload permissions
   - Ensure you haven't exceeded free tier limits

### Debug Steps:
1. Check Flask application logs for error messages
2. Test Cloudinary connection with their API explorer
3. Verify environment variables are loaded correctly

## Security Best Practices

1. **Environment Variables**
   - Never commit API secrets to your repository
   - Use secure environment variable management in production
   - Rotate API keys periodically

2. **Upload Restrictions**
   - The app already includes file type restrictions
   - Consider adding file size limits if needed
   - Monitor upload patterns for abuse

3. **Access Control**
   - Keep API Secret confidential
   - Use signed URLs for sensitive content
   - Consider folder-based access controls

## Support Resources

- **Cloudinary Documentation**: https://cloudinary.com/documentation
- **Python SDK Guide**: https://cloudinary.com/documentation/python_integration
- **Support**: https://support.cloudinary.com/

## Migration Notes

If migrating from another storage service:
1. Existing file URLs will need to be updated
2. Consider running a migration script for existing appointments
3. Test thoroughly before deploying to production

The Cloudinary integration is now ready to use with your Fix and Fit application!
