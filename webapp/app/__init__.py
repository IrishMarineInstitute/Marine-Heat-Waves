from flask import Flask
app = Flask(__name__)

# from werkzeug.debug import DebuggedApplication
# app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.debug = False
from app import views
