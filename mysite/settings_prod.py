from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['anthonystevens.dev', 'www.anthonystevens.dev', '.vercel.app']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'