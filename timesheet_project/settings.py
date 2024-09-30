from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key - use an environment variable for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())

# Debugging
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Allowed hosts
ALLOWED_HOSTS = [
    'timesheet-app-d8y2.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'timesheet_app',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL configuration
ROOT_URLCONF = 'timesheet_project.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'timesheet_app/templates'],  # Updated path for templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application
WSGI_APPLICATION = 'timesheet_project.wsgi.application'

# Database configuration - use PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Change to 'django.db.backends.postgresql' in production
        'NAME': BASE_DIR / 'db.sqlite3',
        # Uncomment and configure for PostgreSQL:
        # 'USER': os.environ.get('DB_USER'),
        # 'PASSWORD': os.environ.get('DB_PASSWORD'),
        # 'HOST': os.environ.get('DB_HOST', 'localhost'),
        # 'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'