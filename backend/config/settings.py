from pathlib import Path
import os

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

env = environ.Env(
    DEBUG=(bool, False),
    MAX_UPLOAD_SIZE_MB=(int, 50),
    DEFAULT_TOP_K=(int, 6),
    RAG_MIN_SCORE=(float, 0.2),
)

if (BASE_DIR / '.env').exists():
    environ.Env.read_env(BASE_DIR / '.env')
elif (ROOT_DIR / '.env').exists():
    environ.Env.read_env(ROOT_DIR / '.env')

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY', default='unsafe-dev-secret-key')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:5173'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'documents',
    'chat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASE_URL = env('DATABASE_URL', default='sqlite:///db.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(env('MEDIA_ROOT', default=str(ROOT_DIR / 'data' / 'uploads')))
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

GOOGLE_API_KEY = env('GOOGLE_API_KEY', default='')
GEMINI_CHAT_MODEL = env('GEMINI_CHAT_MODEL', default='gemini-1.5-flash')
GEMINI_EMBEDDING_MODEL = env('GEMINI_EMBEDDING_MODEL', default='models/text-embedding-004')
CHROMA_PERSIST_DIR = Path(env('CHROMA_PERSIST_DIR', default=str(ROOT_DIR / 'data' / 'chroma')))
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_SIZE_MB = env('MAX_UPLOAD_SIZE_MB')
DEFAULT_TOP_K = env('DEFAULT_TOP_K')
RAG_MIN_SCORE = env('RAG_MIN_SCORE')
