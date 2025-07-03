# Heroku Deployment Guide

This guide will help you deploy your Freebies API backend to Heroku.

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Make sure your code is in a Git repository

## Quick Deployment

### Option 1: Automated Script (Recommended)

1. **Login to Heroku**:

   ```bash
   heroku login
   ```

2. **Run the deployment script**:

   ```bash
   ./deploy.sh
   ```

3. **Follow the prompts** to create a new app or use an existing one.

### Option 2: Manual Deployment

1. **Login to Heroku**:

   ```bash
   heroku login
   ```

2. **Create a new Heroku app**:

   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL database**:

   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set environment variables**:

   ```bash
   heroku config:set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
   heroku config:set ALGORITHM=HS256
   heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Deploy the app**:

   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Run database migrations**:

   ```bash
   heroku run alembic upgrade head
   ```

7. **Open the app**:
   ```bash
   heroku open
   ```

## Environment Variables

The following environment variables are automatically set by the deployment script:

- `DATABASE_URL`: Automatically set by Heroku PostgreSQL addon
- `SECRET_KEY`: Automatically generated secure key
- `ALGORITHM`: Set to "HS256" for JWT tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Set to 30 minutes

## Post-Deployment

### Update Frontend Configuration

After deployment, update your frontend's API URL in `freebies_frontend/app.config.ts`:

```typescript
export const API_URL = "https://your-app-name.herokuapp.com";
```

### Useful Commands

- **View logs**: `heroku logs --tail --app your-app-name`
- **Run commands**: `heroku run <command> --app your-app-name`
- **Open app**: `heroku open --app your-app-name`
- **View config**: `heroku config --app your-app-name`

### API Endpoints

Your API will be available at:

- **Base URL**: `https://your-app-name.herokuapp.com`
- **API Documentation**: `https://your-app-name.herokuapp.com/docs`
- **Health Check**: `https://your-app-name.herokuapp.com/`

## Troubleshooting

### Common Issues

1. **Build fails**: Check the build logs with `heroku logs --tail`
2. **Database connection issues**: Ensure PostgreSQL addon is properly configured
3. **Migration errors**: Run `heroku run alembic upgrade head` manually
4. **Environment variables**: Verify with `heroku config`

### Getting Help

- **Heroku Documentation**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **PostgreSQL on Heroku**: [devcenter.heroku.com/articles/heroku-postgresql](https://devcenter.heroku.com/articles/heroku-postgresql)

## Cost Considerations

- **PostgreSQL Mini**: $5/month (includes 1GB storage)
- **Dynos**: Free tier available for basic usage
- **Add-ons**: Additional costs may apply for advanced features

## Security Notes

- Never commit sensitive information like API keys or database URLs
- Use environment variables for all configuration
- Regularly update dependencies for security patches
- Monitor your app logs for suspicious activity
