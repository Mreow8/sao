from pathlib import Path
import os
# Use only pathlib
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'mainpage.CustomUser'
# Redirects to this URL if @login_required is used without a specific `login_url`
LOGIN_URL = '/login/'  # or the correct path or name
X_FRAME_OPTIONS = "SAMEORIGIN"
STATIC_URL = '/static/'

# This will now work because BASE_DIR is a Path object
STATICFILES_DIRS = [
    BASE_DIR / 'mainpage' / 'static',
]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://localhost:8000",
    "http://localhost:8001",
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# For production or collectstatic command:
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-wqcuti7mokhf)l@v3r0@@xo@(#ss02u8r8_xa6cw0xs96tpxd!'

DEBUG = True

ALLOWED_HOSTS = ["sao-b1fm.onrender.com", "localhost", "127.0.0.1"]

import os
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'mainpage',
    'widget_tweaks',
   "tailwind",
      'captcha',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
# Google reCAPTCHA Keys
RECAPTCHA_PUBLIC_KEY = '6LfhQOcrAAAAANIW45UKBoxv_N6yLJfCCNpyx-j3'
RECAPTCHA_SECRET_KEY = '6LfhQOcrAAAAAE9VIfgc4IoDIlW4y695n3T9INer'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mainpage.middleware.AlumniStatusMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages','mainpage.context_processors.alumni_status_context',
                'mainpage.context_processors.scholarship_status',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'Asia/Manila'  # Or your appropriate timezone


USE_I18N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/



# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ✅ For development only: print emails to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
