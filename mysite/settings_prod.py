from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['anthonystevens.dev', 'www.anthonystevens.dev', '.vercel.app']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'