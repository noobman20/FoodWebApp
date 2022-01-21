# IMPORTS
from flask import Blueprint, render_template, request, flash, jsonify, json
from app import db, requires_roles
from models import User, Foods, Places, Posts
from flask_login import login_required, current_user
import datetime

# CONFIG
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


# VIEWS
# view admin homepage
@admin_blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def admin():

    foods = Foods.query.all()
    places = Places.query.all()

    return render_template('admin_post.html', name=current_user.firstname, food_list=str(foods), place_list=str(places))


@admin_blueprint.route('/admin_food', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def admin_food():
    return render_template('admin_food.html', name=current_user.firstname)


@admin_blueprint.route('/admin_place', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def admin_place():
    return render_template('admin_place.html', name=current_user.firstname)


@admin_blueprint.route('/user_view', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def user_view():
    return render_template('admin_user_view.html', name=current_user.firstname)


@admin_blueprint.route('/query_user', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def query_user():
    page = int(request.form["page"])
    rows = int(request.form["rows"])

    users = User.query.all()
    user = users[(page-1)*rows:page*rows]

    e =dict()
    e["total"] = len(users)
    e["rows"] = json.loads(str(user))

    return jsonify(e)


@admin_blueprint.route('/query_post', methods=['GET', 'POST'])
@login_required
def query_post():
    page = int(request.form["page"])
    rows = int(request.form["rows"])
    posts = db.session.query(Posts, Places, Foods).join(Foods).join(Places).all()

    post = posts[(page - 1) * rows:page * rows]

    my_list = []
    for p in post:
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
    e["total"] = len(posts)
    e["rows"] = my_list

    return jsonify(e)


@admin_blueprint.route('/add_post', methods=['POST'])
@login_required
@requires_roles('admin')
def add_post():
    str_date = datetime.datetime.now().strftime('%Y-%m-%d')
    post = Posts(request.form["food_id"], request.form["place_id"], current_user.id, request.form["amount"], str_date)
    db.session.add(post)
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/update_post', methods=['POST'])
@login_required
@requires_roles('admin')
def update_post():
    id = request.form["id"]
    food_id = request.form["food_id"]
    place_id = request.form["place_id"]
    amount = request.form["amount"]

    post = Posts.query.filter_by(id=id).first()
    post.food_id = int(food_id)
    post.place_id = int(place_id)
    post.user_id = current_user.id
    post.amount = int(amount)

    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/delete_post', methods=['POST'])
@login_required
@requires_roles('admin')
def delete_post():
    id = request.form["id"]

    Posts.query.filter_by(id=id).delete()
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/query_food', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def query_food():
    page = int(request.form["page"])
    rows = int(request.form["rows"])

    foods = Foods.query.all()
    food = foods[(page-1)*rows:page*rows]

    e =dict()
    e["total"] = len(foods)
    e["rows"] = json.loads(str(food))

    return jsonify(e)


@admin_blueprint.route('/add_food', methods=['POST'])
@login_required
@requires_roles('admin')
def add_food():
    food = Foods(request.form["food_name"])
    db.session.add(food)
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/update_food', methods=['POST'])
@login_required
@requires_roles('admin')
def update_food():
    id = request.form["id"]
    food_name = request.form["food_name"]

    Foods.query.filter_by(id=id).update({'food_name' : food_name})
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/delete_food', methods=['POST'])
@login_required
@requires_roles('admin')
def delete_food():
    id = request.form["id"]

    Foods.query.filter_by(id=id).delete()
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/query_place', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def query_place():
    page = int(request.form["page"])
    rows = int(request.form["rows"])

    places = Places.query.all()
    place = places[(page-1)*rows:page*rows]

    e =dict()
    e["total"] = len(places)
    e["rows"] = json.loads(str(place))

    return jsonify(e)


@admin_blueprint.route('/add_place', methods=['POST'])
@login_required
@requires_roles('admin')
def add_place():
    place = Places(request.form["place_name"])
    db.session.add(place)
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/update_place', methods=['POST'])
@login_required
@requires_roles('admin')
def update_place():
    id = request.form["id"]
    place_name = request.form["place_name"]

    Places.query.filter_by(id=id).update({'place_name' : place_name})
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)


@admin_blueprint.route('/delete_place', methods=['POST'])
@login_required
@requires_roles('admin')
def delete_place():
    id = request.form["id"]

    Places.query.filter_by(id=id).delete()
    db.session.commit()

    e = dict()
    e["success"] = True
    return jsonify(e)

