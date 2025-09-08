from flask import Flask
from auth.routes import auth_bp
from admin.routes import admin_bp
from facilitator.routes import facilitator_bp
from participant.routes import participant_bp
from db import mysql
import config

app = Flask(__name__)
app.config.from_object(config)

mysql.init_app(app)

# Регистрация blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

app.register_blueprint(facilitator_bp)
app.register_blueprint(participant_bp)

if __name__ == '__main__':
    app.run(debug=True)
