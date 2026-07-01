# Text2Handwriting Converter

https://text-to2-handwriting.onrender.com
- The website will look like it's loading forever. It usually takes about 30 to 50 seconds for the server to "wake up".
- Once it wakes up, the website will be lightning fast for everyone using it. It only goes back to sleep after 15 straight minutes of zero traffic.

A lightweight, robust web application that converts typed digital text into realistic, customizable handwritten documents. Built with Django and optimized for easy deployment on free cloud hosting platforms like Render or Railway.

## ✨ Features
- **Multi-Language Support**: Converts English, Hindi, and Sanskrit text.
- **Realistic Rendering**: Adjust line variance, word spacing, character spacing, and pressure variance to create unique and natural-looking handwriting.
- **Multiple Output Formats**: Export your generated handwriting as high-quality PNG images or compiled PDF documents.
- **Customizable Layouts**: Fine-tune margins, line spacing, ink color, and paper color. Support for standard page sizes (A4, A5, Letter) and custom dimensions.
- **Cloud-Ready**: Stripped of heavy dependencies (like Celery and GPU-bound PyTorch) and optimized with Python `threading` for seamless deployment on free-tier Web Services.

## 🚀 Tech Stack
- **Backend**: Python 3, Django 4.2
- **Image Processing**: Pillow (PIL), OpenCV-Python-Headless
- **Machine Learning / Synthesis**: PyTorch (CPU-only to save deployment space)
- **Frontend**: HTML5, Bootstrap 5, Custom CSS (Glassmorphism design)
- **Database**: SQLite3 (Local) / PostgreSQL (Production via `dj-database-url`)

## 🛠️ Local Development Setup

If you want to run this project on your local machine, follow these steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/rajguru26-09/text-to-handwriting.git
   cd text-to-handwriting
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   *The app will be available at http://127.0.0.1:8000*

## ☁️ Deployment (Free on Render.com)

This project has been explicitly optimized to run on PaaS providers without requiring paid background workers.

1. Push your code to your GitHub account.
2. Log into [Render.com](https://render.com) and click **New > Web Service**.
3. Connect your GitHub repository.
4. **Configuration**:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn handwriting_project.wsgi:application`
5. **Environment Variables**:
   - `SECRET_KEY`: Enter a long random string.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*` (or your specific Render URL)
6. Click **Create Web Service**. 

*(Note: Render's free tier uses ephemeral storage, so generated images will be cleared when the instance restarts, which is perfect for a temporary conversion tool!)*

## 📝 License
This project is open-source and available under the MIT License.
