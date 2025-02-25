import os
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash
)
from flask_login import login_user, logout_user, login_required
from model.user_service import UserService

auth = Blueprint("auth", __name__, url_prefix="/rp/tester/auth")
auth.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserService.login(username, password)
        if user is not None:
            login_user(user)
            return redirect(url_for('auth.account'))
        else:
            flash('Login failed! Please check your username and password.')
    users = UserService.get_users()
    return render_template('login-page.html', rp_users = users)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/account', methods=['GET'])
@login_required
def account():
    return render_template('account-page.html')
