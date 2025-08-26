# AWS S3 Setup Guide for Fix and Fit

This guide will help you set up AWS S3 for file storage in your Fix and Fit application.

## Prerequisites

- AWS Account (create at https://aws.amazon.com if you don't have one)
- Basic understanding of AWS services

## Step 1: Create an S3 Bucket

1. **Log in to AWS Console**
   - Go to https://console.aws.amazon.com
   - Sign in with your AWS account

2. **Navigate to S3**
   - Search for "S3" in the AWS services search bar
   - Click on "S3" to open the S3 console

3. **Create a New Bucket**
   - Click "Create bucket"
   - Choose a unique bucket name (e.g., `fixandfit-healthcare-files`)
   - Select your preferred AWS region (e.g., `us-east-1`)
   - **Important**: Uncheck "Block all public access" since we need public read access for file downloads
   - Check the acknowledgment box for public access
   - Click "Create bucket"

## Step 2: Configure Bucket Policy for Public Read Access

1. **Open Your Bucket**
   - Click on your newly created bucket name

2. **Set Bucket Policy**
   - Go to the "Permissions" tab
   - Scroll down to "Bucket policy"
   - Click "Edit" and paste this policy (replace `YOUR-BUCKET-NAME` with your actual bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

3. **Save the Policy**
   - Click "Save changes"

## Step 3: Create IAM User for Programmatic Access

1. **Navigate to IAM**
   - Search for "IAM" in the AWS services search bar
   - Click on "IAM" to open the IAM console

2. **Create a New User**
   - Click "Users" in the left sidebar
   - Click "Create user"
   - Enter username: `fixandfit-s3-user`
   - Select "Programmatic access" (API access)
   - Click "Next"

3. **Set Permissions**
   - Choose "Attach policies directly"
   - Search for and select `AmazonS3FullAccess`
   - Click "Next" then "Create user"

4. **Save Credentials**
   - **IMPORTANT**: Copy and save the Access Key ID and Secret Access Key
   - You won't be able to see the Secret Access Key again!

## Step 4: Configure Environment Variables

Add these environment variables to your deployment platform (Vercel, Heroku, etc.):

```bash
AWS_ACCESS_KEY_ID=your-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-secret-access-key-here
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET_NAME=your-bucket-name-here
```

## Step 5: Test the Configuration

1. **Local Testing**
   - Create a `.env` file in your flask-app directory
   - Add the AWS environment variables
   - Run your Flask app locally and test file uploads

2. **Production Testing**
   - Deploy your app with the environment variables set
   - Test file uploads through the appointment booking form

## Security Best Practices

1. **IAM User Permissions**
   - Consider creating a custom policy with minimal required permissions instead of `AmazonS3FullAccess`
   - Regularly rotate access keys

2. **Bucket Security**
   - Enable versioning for backup purposes
   - Consider enabling server-side encryption
   - Monitor access logs

3. **Environment Variables**
   - Never commit AWS credentials to your repository
   - Use secure environment variable management in production

## Cost Optimization

1. **Storage Classes**
   - Use S3 Standard for frequently accessed files
   - Consider S3 Intelligent-Tiering for automatic cost optimization

2. **Lifecycle Policies**
   - Set up lifecycle policies to automatically delete or archive old files
   - Consider moving old appointment files to cheaper storage classes

## Troubleshooting

### Common Issues:

1. **Access Denied Errors**
   - Check bucket policy is correctly configured
   - Verify IAM user has proper permissions
   - Ensure bucket name in policy matches actual bucket name

2. **File Upload Failures**
   - Verify AWS credentials are correctly set in environment variables
   - Check bucket exists and is in the correct region
   - Ensure file size doesn't exceed limits

3. **Public Access Issues**
   - Confirm "Block all public access" is disabled
   - Verify bucket policy allows public read access
   - Check file ACL is set to public-read

## Support

For AWS-specific issues, consult:
- AWS S3 Documentation: https://docs.aws.amazon.com/s3/
- AWS Support: https://aws.amazon.com/support/

For application-specific issues, check the Flask app logs and ensure all environment variables are properly configured.
