from .base import *

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
for docker_host in ("backend", "forum_backend"):
    if docker_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(docker_host)
    
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
