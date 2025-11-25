from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'mainpage.CustomUser'
LOGIN_URL = '/main/login/'
X_FRAME_OPTIONS = "SAMEORIGIN"
STATIC_URL = '/static/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'saoctuargao@gmail.com'
EMAIL_HOST_PASSWORD = 'udylybgizusnhejg'
DEFAULT_FROM_EMAIL = 'saoctuargao@gmail.com'
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
STATIC_ROOT = BASE_DIR / 'staticfiles'
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"
SECRET_KEY = 'django-insecure-wqcuti7mokhf)l@v3r0@@xo@(#ss02u8r8_xa6cw0xs96tpxd!'
DEBUG = True
ALLOWED_HOSTS = ["sao-b1fm.onrender.com", "localhost", "127.0.0.1"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

TAILWIND_APP_NAME = 'theme'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'mainpage',
    'widget_tweaks',
    'theme',
    "tailwind",
    'captcha',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
]
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
    'mainpage.middleware.RoleRestrictionMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mainpage.context_processors.alumni_status_context',
                'mainpage.context_processors.scholarship_status',
                    'mainpage.context_processors.theme_selection',

            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'
USE_TZ = True
TIME_ZONE = 'Asia/Manila'
USE_I1N = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'