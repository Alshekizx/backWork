from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-key-for-dev")


DEBUG = False

ALLOWED_HOSTS = [
    "naijatalk.xyz",
    "www.naijatalk.xyz",
    "api.naijatalk.xyz",
    "naijatalk",
    "localhost",
    "127.0.0.1",
]

FRONTEND_DOMAIN = "https://www.naijatalk.xyz/"

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
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Insert WhiteNoise AFTER security middleware
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

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

# Database - PostgreSQL (local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': "127.0.0.1",
        'NAME': "naijatalk_db",
        'USER': "naijauser",
        'PASSWORD': "StrongPasswordHere",
        'PORT': '5432',
    }
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

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOWED_ORIGINS = [
    "https://www.naijatalk.xyz",
    "https://naijatalk.xyz",

]

CSRF_TRUSTED_ORIGINS = [
    "https://www.naijatalk.xyz",
    "https://naijatalk.xyz",
]

CORS_ALLOW_CREDENTIALS = True



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

# Email - console backend for dev
DEFAULT_FROM_EMAIL = "no-reply@naijatalk.xyz"
ADMIN_EMAIL = "seyiduncan40@gmail.com"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

FIREBASE_SERVICE_ACCOUNT_FILE = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_FILE",
    os.path.join(BASE_DIR, "firebase_service_account.json")  # fallback path
)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
