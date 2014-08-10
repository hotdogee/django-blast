DEBUG = False
TEMPLATE_DEBUG = DEBUG

with open('/etc/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

ALLOWED_HOSTS = (
    'localhost',
)
