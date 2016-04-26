from flask import Flask, render_template, request, redirect, jsonify, url_for
from functools import wraps
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, Item, Category
from flask import session as login_session
import random
import string
import httplib2
import json
from flask import make_response, flash, abort

app = Flask(__name__)

# Create database engine
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Make the database session
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


def login_required(f):
    """ Login required decorator """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if authenticated() == 0:
            abort(401)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login')
def login():
    """ Login routine """
    # Create a random state string
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # Show login page with unique state variable
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """ Connect Facebook account """
    # Check the state variable
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Read the app_id from secret file
    app_id = json.loads(open('fb_client_secret.json', 'r')
                        .read())['web']['app_id']

    # Read the app_secret code form secret file
    app_secret = json.loads(open('fb_client_secret.json', 'r')
                            .read())['web']['app_secret']

    # URL to check the access_token
    url = 'https://graph.facebook.com/oauth/access_token?'\
          'grant_type=fb_exchange_token&client_id=%s&client_secret=%s&'\
          'fb_exchange_token=%s' % (app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Strip expire tag from access token
    token = result.split("&")[0]

    # URL to get user informations (name, id and mail)
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Read data and set login_session variables
    data = json.loads(result)
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Store access_token to login_session for logout
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Check if logged in user (email) already exists
    user_id = checkExistingUser(login_session['email'])
    if user_id is None:
        # If user with logged in email not existing -> create new user
        user_id = newUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    # Create flash message
    flash("Logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """ Disconnect logged in Facebook user """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
          % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "Logged out"


@app.route('/logout')
def logout():
    """ logout routine """
    # Disconnect logged in user
    fbdisconnect()
    # Delete session variables
    del login_session['username']
    del login_session['email']
    del login_session['facebook_id']
    del login_session['access_token']
    del login_session['user_id']
    # Create flash message
    flash('Logout successful.', 'success')
    return redirect(url_for('showCatalog'))


def newUser(login_session):
    """ Create a new app user """
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    # Return user id of created user
    return user.id


def checkExistingUser(email):
    """ Checks whether a user exists with a specified email address """
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def authenticated():
    """ Returns the id of a logged in user. If no user logged in, return 0 """
    if 'user_id' in login_session and 'access_token' in login_session:
        user = db_session.query(User).filter_by(
            id=login_session['user_id']).one()
        if user is not None:
            return user.id
    return 0


def editable(itemOrCategory):
    """ Returns whether the item/category was created by the logged in user """
    user_id = authenticated()

    # If a user is logged in and this user is the creator of the item/category
    if user_id != 0 and itemOrCategory.creator_id == user_id:
        # Item or category is editable
        return True

    return False


@app.route('/catalog/<int:category_id>/JSON')
def catalogJSON(category_id):
    """ Returns all categories with items in JSON format """
    try:
        categories = db_session.query(Category).filter_by(id=category_id).one()
        items = db_session.query(Item).filter_by(category_id=category_id).all()
        return jsonify(Category=categories.serialize,
                       Items=[i.serialize for i in items])
    except NoResultFound:
        return '[404]'


@app.route('/')
@app.route('/catalog')
def showCatalog():
    """ Shows all categories and the latest items """
    categories = db_session.query(Category).all()
    latestItems = db_session.query(Item).order_by(desc(Item.id)).limit(10)
    return render_template('viewCatalog.html', categories=categories,
                           items=latestItems, editable=editable)


@app.route('/catalog/category/<int:category_id>')
def showCategory(category_id):
    """ Shows all items of a specified category """
    categories = db_session.query(Category).all()
    category = db_session.query(Category).filter_by(id=category_id).one()
    # Get all items of the specified category
    categoryItems = db_session.query(Item).filter_by(
        category_id=category_id).all()
    return render_template('viewCatalog.html',
                           categories=categories,
                           items=categoryItems,
                           category=category,
                           editable=editable)


@app.route('/catalog/item/<int:item_id>')
def showItem(item_id):
    """ Shows an existing item """
    item = db_session.query(Item).filter_by(id=item_id).one()
    return render_template('viewItem.html', item=item, editable=editable)


@app.route('/catalog/category/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    """ Creates a new category """
    if request.method == 'POST':
        # Create the new category object
        newCategory = Category(name=request.form['name'],
                               creator_id=login_session['user_id'])
        db_session.add(newCategory)
        db_session.commit()
        # Create flash message
        flash("New category %s created." % request.form['name'])
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCategory.html')


@app.route('/catalog/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
    """ Creates a new item """
    if request.method == 'POST':
        # Create the new item object
        newItem = Item(title=request.form['title'],
                       description=request.form['description'],
                       price=request.form['price'],
                       category_id=request.form['category_id'],
                       creator_id=login_session['user_id'])
        db_session.add(newItem)
        db_session.commit()
        # Create flash message
        flash("New item %s created." % request.form['title'])
        return redirect(url_for('showCatalog'))
    else:
        categories = db_session.query(Category).all()
        return render_template('newItem.html', categories=categories)


@app.route('/catalog/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """ Edits an existing category """
    editCategory = db_session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        # Check the changed members
        if request.form['name']:
            editCategory.name = request.form['name']
        db_session.add(editCategory)
        db_session.commit()
        # Create flash message
        flash("Category %s edited." % request.form['name'])
        return redirect(url_for('showCatalog'))
    else:
        return render_template('editCategory.html', category=editCategory)


@app.route('/catalog/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    """ Edits an existing item """
    editItem = db_session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        # Check the changed members
        if request.form['title']:
            editItem.title = request.form['title']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['price']:
            editItem.price = request.form['price']
        if request.form['category_id']:
            editItem.course = request.form['category_id']
        db_session.add(editItem)
        db_session.commit()
        # Create flash message
        flash("Item %s edited." % request.form['title'])
        return redirect(url_for('showCatalog'))
    else:
        categories = db_session.query(Category).all()
        return render_template('editItem.html',
                               item=editItem,
                               categories=categories)


@app.route('/catalog/category/<int:category_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """ Deletes an existing category """
    deleteCategory = db_session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        # Save name for the flash message
        name = deleteCategory.name
        db_session.query(Item).filter_by(category_id=category_id).delete()
        db_session.delete(deleteCategory)
        db_session.commit()
        # Create flash message
        flash("Category %s deleted." % name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCategory.html', category=deleteCategory)


@app.route('/catalog/item/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_id):
    """ Deletes an existing item """
    deleteItem = db_session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        # Save title for the flash message
        title = deleteItem.title
        db_session.delete(deleteItem)
        db_session.commit()
        # Create flash message
        flash("Item %s deleted." % title)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteItem.html', item=deleteItem)


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.debug = False
    app.run(host='0.0.0.0', port=8000)
