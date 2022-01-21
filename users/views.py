# IMPORTS
import datetime
import logging
from functools import wraps
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from werkzeug.security import check_password_hash
from flask_login import current_user, login_user, logout_user, UserMixin, login_required

from app import db, requires_roles
from models import User, Foods, Places, Posts, Takens
from users.forms import RegisterForm, LoginForm
import pyotp
import json
from flask import Flask, jsonify

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        logging.warning('SECURITY - User registration [%s, %s]', form.email.data, request.remote_addr)

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('logins'):
        session['logins'] = 0
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    form = LoginForm()

    if form.validate_on_submit():

        session['logins'] += 1

        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')
            flash('Please check your login details and try again')

            logging.warning('SECURITY - Invalid login attempts [%s, %s]', form.email.data, request.remote_addr)

            return render_template('login.html', form=form)

        #if pyotp.TOTP(user.pin_key).verify(form.pin.data):

        session['logins'] = 0

        login_user(user)

        user.last_logged_in = user.current_logged_in
        user.current_logged_in = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()

        logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)

        if current_user.role == 'admin':
            return redirect(url_for('admin.admin'))
        else:
             return redirect(url_for('users.profile'))


    return render_template('login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
@login_required
@requires_roles('user')
def profile():
    return render_template('profile.html', name=current_user.firstname)


# view user food
@users_blueprint.route('/food')
@login_required
@requires_roles('user')
def food():

    return render_template('user_food.html', name=current_user.firstname)


# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)


@users_blueprint.route('/logout')
@login_required
def logout():

    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)

    logout_user()
    return redirect(url_for('index'))


@users_blueprint.route('/taken_post', methods=['POST'])
@login_required
@requires_roles('user')
def taken_post():
    str_date = datetime.datetime.now().strftime('%Y-%m-%d')
    takens = Takens.query.filter_by(post_time=str_date).filter_by(user_id=current_user.id).all()

    if len(takens) == 5:
        e = dict()
        e["errorMsg"] = "max taken 5 everyday"
        return jsonify(e)

    id = request.form["id"]

    post = Posts.query.filter_by(id=id).first()
    if post.amount == 0:
        e = dict()
        e["errorMsg"] = "this food amount is 0"
        return jsonify(e)

    post.amount = post.amount-1

    str_date = datetime.datetime.now().strftime('%Y-%m-%d')
    taken = Takens(post.food_id, post.place_id, current_user.id, 1, str_date, id)
    db.session.add(taken)

    db.session.commit()


    e = dict()
    e["success"] = True
    return jsonify(e)


@users_blueprint.route('/query_taken', methods=['POST'])
@login_required
@requires_roles('user')
def query_taken():
    str_date = datetime.datetime.now().strftime('%Y-%m-%d')
    page = int(request.form["page"])
    rows = int(request.form["rows"])
    takens = db.session.query(Takens, Places, Foods).join(Foods).join(Places).filter(Takens.post_time==str_date).filter(Takens.user_id==current_user.id).all()

    taken = takens[(page - 1) * rows:page * rows]

    my_list = []
    for p in taken:
        d = dict()
        d["id"] = p[0].id
        d["food_id"] = p[0].food_id
        d["food_name"] = p[2].food_name
        d["place_id"] = p[0].place_id
        d["place_name"] = p[1].place_name
        d["amount"] = p[0].amount
        d["post_time"] = p[0].post_time
        my_list.append(d)


    e = dict()
    e["total"] = len(takens)
    e["rows"] = my_list

    return jsonify(e)