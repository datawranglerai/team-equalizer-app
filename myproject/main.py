from myproject.wsgi import application

# Google App Engine by default looks for a main.py file at the root of the app
# directory with a WSGI-compatible object called app.
# This file imports the WSGI-compatible object of the Django app,
# application from myproject/wsgi.py and renames is app so it is
# discoverable by App Engine without additional configuration.
# Alternatively, you can add a custom entrypoint field in your app.yaml:
# entrypoint: gunicorn -b :$PORT myproject.wsgi

app = application
