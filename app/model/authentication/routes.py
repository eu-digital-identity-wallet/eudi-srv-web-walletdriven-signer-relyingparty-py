# coding: latin-1
###############################################################################
# Copyright 2025 European Commission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

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
