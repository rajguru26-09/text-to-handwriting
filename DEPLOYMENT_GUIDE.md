# Deployment Guide

This project has been optimized to be deployed easily and for free on modern platform-as-a-service (PaaS) providers such as Render, Railway, or Heroku.

## Optimizations Made for Web Deployment

1. **Removed Celery Dependency**: Celery requires an external message broker (like Redis) and an extra worker process, which is often not free. Background processing has been replaced with Python's native `threading` module, meaning this application will run flawlessly on a single free web dyno.
2. **CPU-only PyTorch**: Deploying standard PyTorch pulls heavy CUDA (GPU) dependencies (~2GB+) which frequently break free tier limits. The `requirements.txt` has been updated to use `torch` CPU wheels exclusively, bringing the size drastically down.
3. **Database Configuration**: Added `psycopg2-binary` and configured `dj-database-url` so the app automatically connects to PostgreSQL in production when `DATABASE_URL` is set, but uses `db.sqlite3` locally.
4. **Environment Variables**: No sensitive API keys or Django SECRET_KEYs are hardcoded.

## How to Deploy (e.g., on Render.com for Free)

1. **Push to GitHub**:
   Commit everything and push the codebase to your GitHub account.

2. **Connect to Render**:
   - Go to [Render.com](https://render.com) and create a New **Web Service**.
   - Connect your GitHub repository.

3. **Configure the Service**:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn handwriting_project.wsgi:application`
   - **Plan**: Free

4. **Environment Variables**:
   Under the "Environment" tab, set the following variables:
   - `SECRET_KEY`: Set this to a long random string.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*` (or your app's specific URL like `yourapp.onrender.com`)
   - `DATABASE_URL`: (Optional) If you create a free PostgreSQL database on Render, paste its Internal Database URL here. Otherwise, the app will run with a temporary SQLite database (note: SQLite data gets wiped when Render puts the free service to sleep).

5. **Deploy**:
   Click "Create Web Service" and wait for the build to finish. Your text-to-handwriting application is now live!
