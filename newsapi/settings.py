from pathlib import Path
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-key-for-dev")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1"]

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "naijatalkbackend.onrender.com",  # Render backend
    "backwork-9ddv.onrender.com",          # Render service name
]

FRONTEND_DOMAIN = "https://naijatalk.xyz"

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_extensions",
    "rest_framework",
    "news",
    "rest_framework.authtoken",
    "djoser",
    "multiselectfield",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "newsapi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "newsapi.wsgi.application"

# Database (Render provides DATABASE_URL automatically)
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600
    )
}

AUTH_USER_MODEL = "news.CustomUser"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (Render expects collected files in /staticfiles)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://naijatalk.vercel.app",
    "https://naijatalk-as40bpbhz-alshekizxs-projects.vercel.app",
    "https://naijatalk-c9wnwzhnk-alshekizxs-projects.vercel.app",
    "https://www.naijatalk.xyz",
    "https://naijatalk.xyz",
]
CORS_ALLOW_CREDENTIALS = True

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "https://naijatalk-c9wnwzhnk-alshekizxs-projects.vercel.app",
    "https://naijatalk-as40bpbhz-alshekizxs-projects.vercel.app",
    "https://naijatalk.vercel.app",
    "https://www.naijatalk.xyz",
    "https://naijatalk.xyz",
    "https://naijatalkbackend.onrender.com",
    "https://backwork.onrender.com",
]

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ]
}

DJOSER = {
    "USER_ID_FIELD": "id",
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user_create": "news.serializers.CustomUserCreateSerializer",
        "user": "news.serializers.CustomUserSerializer",
        "current_user": "news.serializers.CustomUserSerializer",
    },
}

# Email (SendGrid for Render)
DEFAULT_FROM_EMAIL = "no-reply@naijatalk.com"
ADMIN_EMAIL = "seyiduncan40@gmail.com"

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_ECHO_TO_STDOUT = True
