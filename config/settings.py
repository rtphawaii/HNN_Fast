from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url

load_dotenv()  # make sure this is near the top

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "changeme")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("true", "1")

# ✅ Fix: split the comma-separated host list
ALLOWED_HOSTS = os.getenv("RENDER_EXTERNAL_HOSTNAME", "127.0.0.1,localhost").split(",")


CSRF_TRUSTED_ORIGINS = [
    f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', '')}"
] if os.getenv("RENDER_EXTERNAL_HOSTNAME") else []

# Project root: HNN_FAST/
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------- Installed apps ----------------- #

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'HNN_Fast',
]

# ----------------- Static files ----------------- #

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# If you use the assets/ folder:
STATICFILES_DIRS = [
    BASE_DIR / "assets",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ----------------- URLs / Templates / WSGI ----------------- #

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # will be overridden below
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]

WSGI_APPLICATION = 'config.wsgi.application'

# ----------------- Database ----------------- #

default_sqlite = "sqlite:///" + str(BASE_DIR / "db.sqlite3")

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", default_sqlite),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ----------------- Auth / i18n ----------------- #

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
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
