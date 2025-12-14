import os
import secrets
import string
from django.db import models
from django.conf import settings

def generate_permalink():
	characters = string.digits + string.ascii_letters
	return ''.join(secrets.choice(characters) for _ in range(20))

def random_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    rand_folder = secrets.token_urlsafe(8)
    rand_name = secrets.token_urlsafe(16)
    return f'files/{rand_folder}/{rand_name}{ext}'