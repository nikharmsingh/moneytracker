# Deployment Guide

[Home](index.md) | [User Guide](user-guide.md) | [Technical Docs](technical-docs.md) | [Development Guide](development-guide.md) | [Deployment Guide](deployment-guide.md) | [FAQ](faq.md)

This guide provides instructions for deploying the Money Tracker application to various environments.

## Table of Contents

- [Deployment Prerequisites](#deployment-prerequisites)
- [Deploying to Render.com](#deploying-to-rendercom)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Backup and Recovery](#backup-and-recovery)

## Deployment Prerequisites

Before deploying Money Tracker, ensure you have:

1. **A MongoDB Atlas account** (or another MongoDB hosting solution)
2. **Your application code in a Git repository** (GitHub, GitLab, etc.)
3. **A Render.com account** (or another hosting platform)
4. **Required environment variables** (see [Environment Variables](#environment-variables))

## Deploying to Render.com

Render.com provides an easy way to deploy Flask applications with MongoDB integration.

### Step 1: Create a Render.com Account

1. Sign up at [Render.com](https://render.com)
2. Verify your email address
3. Connect your GitHub account (or other Git provider)

### Step 2: Create a New Web Service

1. From your Render dashboard, click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Select the branch to deploy (usually `main` or `master`)

### Step 3: Configure the Service

Configure your web service with the following settings:

- **Name**: `money-tracker` (or your preferred name)
- **Environment**: `Python`
- **Region**: Choose the region closest to your users
- **Branch**: `main` (or your default branch)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: Choose an appropriate plan (Free tier works for testing)

### Step 4: Set Environment Variables

Add the following environment variables in the "Environment" tab:

- `FLASK_APP`: `app.py`
- `FLASK_ENV`: `production`
- `SECRET_KEY`: Generate a secure random string
- `MONGODB_URI`: Your MongoDB connection string

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Once complete, you can access your application at the provided URL

### Step 6: Verify Deployment

1. Visit your application URL
2. Verify that you can register, log in, and use all features
3. Check the logs for any errors

## Environment Variables

Money Tracker requires the following environment variables:

| Variable      | Description                              | Example                                                             |
| ------------- | ---------------------------------------- | ------------------------------------------------------------------- |
| `FLASK_APP`   | The main application file                | `app.py`                                                            |
| `FLASK_ENV`   | The environment (development/production) | `production`                                                        |
| `SECRET_KEY`  | Secret key for session encryption        | `your-secure-random-string`                                         |
| `MONGODB_URI` | MongoDB connection string                | `mongodb+srv://username:password@cluster.mongodb.net/money_tracker` |

### Generating a Secure Secret Key

You can generate a secure random string for your `SECRET_KEY` using Python:

```python
import os
import base64

# Generate a 24-byte random string
random_bytes = os.urandom(24)
secret_key = base64.b64encode(random_bytes).decode('utf-8')
print(secret_key)
```

## Database Setup

### MongoDB Atlas Setup

1. **Create a MongoDB Atlas account**:

   - Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a new organization if needed

2. **Create a new project**:

   - Click "New Project"
   - Name your project (e.g., "Money Tracker")
   - Click "Create Project"

3. **Create a new cluster**:

   - Click "Build a Cluster"
   - Choose the free tier option
   - Select your preferred cloud provider and region
   - Click "Create Cluster"

4. **Create a database user**:

   - Go to "Database Access" under Security
   - Click "Add New Database User"
   - Choose Password authentication
   - Enter a username and password
   - Set appropriate privileges (readWrite on the money_tracker database)
   - Click "Add User"

5. **Configure network access**:

   - Go to "Network Access" under Security
   - Click "Add IP Address"
   - For development, you can add your current IP
   - For production with Render, you can add `0.0.0.0/0` (allow from anywhere)
   - Click "Confirm"

6. **Get your connection string**:
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Select "Python" as your driver
   - Copy the connection string
   - Replace `<password>` with your database user's password
   - Replace `myFirstDatabase` with `money_tracker`

### Database Initialization

The Money Tracker application will automatically create the necessary collections when it first runs. No additional setup is required.

## Monitoring and Maintenance

### Monitoring Your Application

1. **Render Dashboard**:

   - Monitor application status
   - View logs for errors
   - Check resource usage

2. **MongoDB Atlas Monitoring**:
   - Monitor database performance
   - Set up alerts for high usage
   - Check connection statistics

### Health Check Endpoint

Money Tracker includes a `/health` endpoint that returns the status of the application and database connection. You can use this endpoint for monitoring:

```
GET /health
```

Response:

```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2023-05-01T12:34:56Z"
}
```

### Updating Your Application

To update your deployed application:

1. Push changes to your GitHub repository
2. Render will automatically detect changes and redeploy
3. Monitor the deployment logs for any issues

For manual deployment:

1. Go to your web service in the Render dashboard
2. Click "Manual Deploy"
3. Select "Deploy latest commit"

## Backup and Recovery

### Database Backups

MongoDB Atlas provides automated backups:

1. **Configure backup schedule**:

   - Go to your cluster settings
   - Click on "Backup"
   - Configure your backup schedule

2. **Restore from backup**:
   - Go to the "Backup" section
   - Select the backup point you want to restore
   - Click "Restore"

### Manual Data Export

You can also manually export data from the application:

1. Use the "Export as CSV" feature in the Transactions page
2. Download and store these files securely

### Disaster Recovery

In case of application failure:

1. **Check application logs** in Render dashboard
2. **Verify database connection** using the health check endpoint
3. **Rollback to previous deployment** if needed
4. **Restore database** from backup if data is corrupted

## Custom Domain Setup

To use a custom domain with your Render deployment:

1. **Add your domain in Render**:

   - Go to your web service
   - Click on "Settings"
   - Scroll to "Custom Domain"
   - Click "Add Custom Domain"
   - Enter your domain name

2. **Configure DNS**:

   - Add a CNAME record pointing to your Render URL
   - Or follow Render's instructions for apex domains

3. **Enable HTTPS**:
   - Render automatically provisions SSL certificates
   - No additional configuration is needed

## Scaling Your Application

As your user base grows, you may need to scale your application:

1. **Upgrade your Render plan**:

   - Go to your web service
   - Click on "Settings"
   - Scroll to "Instance Type"
   - Select a higher tier

2. **Scale your MongoDB Atlas cluster**:

   - Go to your cluster
   - Click "Modify"
   - Choose a higher tier or add more storage

3. **Consider adding caching**:
   - Implement Redis for session storage
   - Cache frequently accessed data
