"""Compatibility module for Gunicorn deployments.

Some platforms default to ``gunicorn app:app``. This module exposes the
Django WSGI application under that name so the deployment can start even if
the runtime command is not updated.
"""

from config.wsgi import application as app
