from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
citizen_bp = Blueprint('citizen', __name__)
admin_bp = Blueprint('admin', __name__)
main_bp = Blueprint('main', __name__)

from . import auth, citizen, admin, main
