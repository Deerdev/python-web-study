# coding=utf-8
from flask import Blueprint

# 归类url前缀
bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/')
def index():
    return 'User"s Index page'
