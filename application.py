from flask import (Flask, render_template,
                   request, redirect, jsonify, url_for, flash)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import os
import bleach
from functools import wraps
from werkzeug.utils import secure_filename
from boto3.s3.transfer import S3Transfer
import boto3
import re
import requests
import json
from flask_sslify import SSLify
from yelpapi import YelpAPI

application = Flask(__name__)
sslify = SSLify(application)

application.config['UPLOAD_FOLDER'] = '/static/img/'
application.config['ALLOWED_EXTENSIONS'] = set(['txt',
                                        'pdf',
                                        'png',
                                        'jpg',
                                        'jpeg',
                                        'gif'])

application.secret_key = 'super_secret_key'
application.config['LOCATION_TYPES'] = {"rec": Recreation,
                                "food": Restaurant,
                                "school": School}

application.config['DEFAULT_CENTER'] = {"lat": 40.688885, "lng": -73.977042}

application.config['AWS_ICON_SOURCE'] = ''

application.config['STATE'] = ''.join(
                                random.choice(string.ascii_uppercase +
                                              string.digits) for x in range(32)
                                )
application.config['EG'] = os.environ['DB_KEY']
application.config['AWS_KEY'] = os.environ['AWS_KEY']
application.config['AWS_SECRET'] = os.environ['AWS_SECRET']
application.config['YELP_API_KEY'] = os.environ['YELP_API_KEY']
application.config['ALLOWED_DOMAIN'] = os.environ['ALLOWED_DOMAIN']

# Connect to Database and create database session
engine = create_engine(application.config['EG'])
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in login_session:
            return f(*args, **kwargs)
        else:
            flash("you are not allowed to access that page")
            return redirect(url_for('showLocations'))
    return decorated_function


@application.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(application.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@application.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@application.route('/fbconnect', methods=['POST'])
def fbconnect():
    user_data = request.get_json(silent=True)
    login_session['provider'] = 'facebook'
    login_session['username'] = user_data['name']
    login_session['email'] = user_data['email']
    login_session['facebook_id'] = user_data['id']
    login_session['picture'] = """
                https://graph.facebook.com/{id}/picture?type=square
            """.format(id=user_data['id'])

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """
        " style="width: 300px;
                height: 300px;border-radius:
                150px;-webkit-border-radius:
                150px;-moz-border-radius: 150px;"> """

    flash("Now logged in as %s" % login_session['username'])
    return output


@application.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included
    # to successfully log out
    access_token = login_session['access_token']
    url = """
        https://graph.facebook.com/%s/permissions?access_token=%s""" % (
                                        facebook_id,
                                        access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been loggged out"


# not fully implemented
@application.route('/igconnect', methods=['GET'])
def igconnect():
    if request.args.get('code'):
        code = request.args.get('code')
        return "code: " + code + " state: " + login_session['state']


@application.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconect()
            del login_session['gplus_id']
            del login_session['credentials']
        # if login_session['provider']  =  =  'facebook':
        #     fbdisconnect()
        #     del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have been successfully logged out.")
        return redirect(url_for('showLocations'))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for('showLocations'))


# JSON API to view Location Information
@application.route('/locations/JSON')
def locationsJSON():
    locations = session.query(Location).filter_by(active="yes").order_by('menuLabel').all()
    response = jsonify(mapLocations=[i.serialize for i in locations])
    response.headers.add('Access-Control-Allow-Origin',
                         application.config['ALLOWED_DOMAIN'])
    return response

# JSON API to view Yelp info
@application.route('/yelp/<string:label>/JSON')
def yelpJSON(label):
    label = label.encode('utf-8')
    yelp_api = YelpAPI(application.config['YELP_API_KEY'])
    result = yelp_api.business_query(label)
    reviews = yelp_api.reviews_query(label)
    result['review_list'] = reviews
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin',
                         application.config['ALLOWED_DOMAIN'])
    return response


# JSON api to search yelp
@application.route('/yelp_search/<string:term>/<string:location>/JSON')
def yelpSearch(term, location):
    yelp_api = YelpAPI (application.config['YELP_API_KEY'])
    result = yelp_api.search_query(term=term,location=location)
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin',
                         application.config['ALLOWED_DOMAIN'])
    return response


# get locations by type (rec, school, food)
@application.route('/locations/<string:location_type>/JSON')
def locationTypeJSON(location_type):
    locations = session.query(Location).filter_by(
                                            active="yes",
                                            type=location_type).order_by('menuLabel').all()

    response = jsonify(mapLocations=[i.serialize for i in locations])
    response.headers.add('Access-Control-Allow-Origin',
                         application.config['ALLOWED_DOMAIN'])
    return response


# get location by id
@application.route('/location/<int:location_id>/JSON')
def locationJSON(location_id):
    location = session.query(Location).filter_by(id=location_id).one()
    return jsonify(Location=[location.serialize])


# get all users
@application.route('/users/JSON')
def usersJSON():
    users = session.query(User).all()
    response = jsonify(users=[i.serialize for i in users])
    response.headers.add(
                            'Access-Control-Allow-Origin',
                            application.config['ALLOWED_DOMAIN'])
    return response


# get user by id
@application.route('/user/<int:user_id>/JSON')
def userJSON(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return jsonify(User=[user.serialize])


# get all reviews
@application.route('/reviews/JSON')
def reviewsJSON():
    reviews = session.query(Review).all()
    response = json(reviews=[i.serialize for i in reviews])
    response.headers.add(
                            'Access-Control-Allow-Origin',
                            application.config['ALLOWED_DOMAIN'])
    return response


# get reviews by user id
@application.route('/user/<int:user_id>/reviews/JSON')
def userReviewsJSON(user_id):
    reviews = session.query(Review).filter_by(user_id=user_id).all()
    response = jsonify(reviews=[i.serialize for i in reviews])
    response.headers.add(
                            'Access-Control-Allow-Origin',
                            application.config['ALLOWED_DOMAIN'])
    return response


# get reviews by location_id
@application.route('/location/<int:location_id>/reviews/JSON')
def locationReviewsJSON(location_id):
    reviews = session.query(Review).filter_by(location_id=location_id).all()
    response = jsonify(reviews=[i.serialize for i in reviews])
    response.headers.add(
                            'Access-Control-Allow-Origin',
                            application.config['ALLOWED_DOMAIN'])
    return response


# Show all locations
@application.route('/')
@application.route('/locations/')
def showLocations():
    locations = session.query(Location).order_by('menuLabel').all()
    if 'username' in login_session:
        currUserId = login_session['user_id']
    else:
        currUserId = ""
    # for location in locations:
    #     location.numReviews = session.query(Review).filter_by(
    #                                    location_id=location.id).count()
    return render_template(
                            'locations.html',
                            locations=locations,
                            currUserId=currUserId,
                            locationHeader="All Locations")


@application.route('/privacypolicy')
def privacyPolicy():
    return render_template('privacypolicy.html')


# filter locations by type
@application.route('/locations/<string:location_type>/')
def locationType(location_type):
    locations = session.query(Location).filter_by(
                                                    type=location_type
                                                 ).order_by('menuLabel').all()

    for location in locations:
        location.numReviews = session.query(Review).filter_by(
                                                    location_id=location.id
                                                    ).count()
    locationNames = {
                        "food": "Restaurants",
                        "rec": "Recreation",
                        "school": "Schools"
                    }
    if 'username' in login_session:
        currUserId = login_session['user_id']
    else:
        currUserId = ""
    return render_template(
                            'locations.html',
                            locations=locations,
                            currUserId=currUserId,
                            locationHeader=locationNames[location_type])

def map_yelp_review_data(json_obj):
    return {
                "total_reviews": json_obj['total'],
                "review": json_obj['reviews'][0]['text'],
                "reviewer": json_obj['reviews'][0]['user']['name']
            }

def map_yelp_data(json_obj):
    display_address = json_obj['location']['display_address']
    tenths = int((json_obj['rating']*10) % 10)
    if (tenths >= 5):
        half_star = 1
    else:
        half_star = 0
    if (len(json_obj['location']['cross_streets']) > 0):
        display_address.append("b/w %s" % json_obj['location']['cross_streets'])
    if 'price' in json_obj:
        cost = len(json_obj['price'])
    else:
        cost = 0
    return {
                "image_url": json_obj['photos'],
                "display_phone": json_obj['display_phone'],
                "display_address": display_address,
                "stars": int(json_obj['rating']),
                "half_star": half_star,
                "url": json_obj['url'],
                "cost": cost
            }

def get_yelp_info(yelp_id):
    auth_headers = { 'Authorization': 'Bearer %s' % application.config['YELP_API_KEY']}
    url = 'https://api.yelp.com/v3/businesses/%s' % yelp_id
    r = requests.get(url, headers=auth_headers)
    if ('error' in r.json()):
        return r.json()
    else:
        return map_yelp_data(r.json())

def get_yelp_reviews(yelp_id):
    yelp_id = yelp_id.encode("utf-8")
    auth_headers = { 'Authorization': 'Bearer %s' % application.config['YELP_API_KEY']}
    r = requests.get('https://api.yelp.com/v3/businesses/%s/reviews' % yelp_id, headers=auth_headers)
    return map_yelp_review_data(r.json())

# Show specific location
@application.route('/location/<int:location_id>')
def showLocation(location_id):
    location = session.query(Location).filter_by(id=location_id).one()
    location.numReviews = session.query(Review).filter_by(
                                        location_id=location.id).count()
    location.locator = session.query(User).filter_by(id=location.user_id).one()
    if 'username' in login_session:
        currUserId = login_session['user_id']
    else:
        currUserId = ""

    if (location.type == 'food'):
        location.meta_info = get_yelp_info(location.yelp_id)
        if ('error' not in location.meta_info):
            reviews = get_yelp_reviews(location.yelp_id)
            location.meta_info['reviews'] = reviews
    else:
        location.meta_info = {}
    return render_template(
                            'showLocation.html',
                            location=location,
                            currUserId=currUserId)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in application.config['ALLOWED_EXTENSIONS']


@application.route('/location/new', methods=['GET', 'POST'])
@login_required
def newLocation():
    if request.method == 'POST':
        newLocation = getNewLocationTypeFromString(
                            request.form["locationType"])
        newLocation = addFormDataToLocation(
                            request.form, request.files, newLocation)
        newLocation.user_id = login_session['user_id']
        session.add(newLocation)
        session.commit()
        flash(newLocation.menuLabel + " added")
        return redirect(url_for("showLocations"))
    else:
        location = Location()
        # defaults
        location.type = "rec"
        location.lat = application.config['DEFAULT_CENTER']['lat']
        location.lng = application.config['DEFAULT_CENTER']['lng']
        return render_template(
                                'editLocation.html',
                                location=location,
                                newLoc=True)


@application.route('/location/<location_id>/review/new', methods=['GET', 'POST'])
@login_required
def newReview(location_id):
    currUserId = login_session['user_id']
    if request.method == 'POST':
        review = Review(review_text=bleach.clean(request.form['review']),
                        location_id=location_id,
                        user_id=login_session['user_id'])
        session.add(review)
        session.commit()
        return redirect(url_for(
                                "newReview",
                                location_id=location_id,
                                currUserId=currUserId
                                ))
    else:
        location = session.query(Location).filter_by(id=location_id).one()
        reviews = session.query(Review).filter_by(
                                    location_id=location_id).all()
        for review in reviews:
            review.reviewer = session.query(User).filter_by(
                                    id=review.user_id).one()
        return render_template(
                                'editLocation.html',
                                location=location,
                                reviews=reviews,
                                currUserId=currUserId,
                                newReview=True)


@application.route('/location/<location_id>/review/<review_id>/delete',
           methods=['GET'])
@login_required
def deleteReview(location_id, review_id):
    review = session.query(Review).filter_by(id=review_id).one()
    if login_session['user_id'] != review.user_id:
        return redirect(url_for('showLocations'))
    session.delete(review)
    session.commit()
    return redirect(url_for("newReview", location_id=location_id))


@application.route('/location/<location_id>/review/<review_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editReview(location_id, review_id):
    review = session.query(Review).filter_by(id=review_id).one()
    if login_session['user_id'] != review.user_id:
        return redirect(url_for('showLocations'))
    location = session.query(Location).filter_by(id=location_id).one()
    currUserId = login_session['user_id']
    if request.method == 'POST':
        review.review_text = bleach.clean(request.form['review'])
        session.commit()
        reviews = session.query(Review).filter_by(
                                                    location_id=location_id
                                                 ).all()
        for review in reviews:
            review.reviewer = session.query(User).filter_by(
                                                    id=review.user_id).one()
        return render_template(
                                'editLocation.html',
                                review=review,
                                location=location,
                                reviews=reviews,
                                newReview=True,
                                editReview=False,
                                currUserId=currUserId)
    else:
        reviews = session.query(Review).filter_by(
                                            location_id=location_id).all()
        for review in reviews:
            review.reviewer = session.query(User).filter_by(
                                            id=review.user_id).one()
        return render_template(
                                'editLocation.html',
                                review=review,
                                location=location,
                                reviews=reviews,
                                newReview=True,
                                editReview=True,
                                currUserId=currUserId)


# This route is expecting a parameter containing the name
# of a file. Then it will locate the file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be shown after the upload
@application.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(application.config['UPLOAD_FOLDER'], filename)


def getNewLocationTypeFromString(locType):
    return application.config['LOCATION_TYPES'][locType]()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# called from edit and new location forms
def addFormDataToLocation(data, imageData, location):
    if 'activeToggle' in data and data['activeToggle'] == "on":
        location.active = "yes"
    else:
        location.active = "no"
    if data['menuLabel']:
        location.menuLabel = bleach.clean(data['menuLabel'])
    if data['fullLabel']:
        location.label = bleach.clean(data['fullLabel'])
    if (
            data['locationType'] == 'school' or
            data['locationType'] == 'rec') and data['wiki_id']:
        location.wiki_id = bleach.clean(data['wiki_id'])
    if data['locationType'] == 'food' and data['yelp_id']:
        location.yelp_id = bleach.clean(data['yelp_id'])
    if data['lat']:
        location.lat = data['lat']
    if data['lng']:
        location.lng = data['lng']
    file = None
    if (imageData):
        file = imageData['file']
    if file and allowed_file(file.filename):
        s3 = boto3.client('s3',
                          aws_access_key_id=application.config['AWS_KEY'],
                          aws_secret_access_key=application.config['AWS_SECRET']
                          )

        if location.menuLabel:
            valids = re.sub(r"[^A-Za-z]+", '', location.menuLabel)
            edited_filename = ("%s_%s" % (valids.lower(), id_generator()))
        else:
            edited_filename = id_generator()
        filename = secure_filename(file.filename)
        BUCKET = 'andrewdunn-pictures'
        s3.put_object(Bucket=BUCKET,
                      Key= "images/%s" % edited_filename,
                      Body=file,
                      ACL='public-read',
                      Metadata={
                        "name": filename,
                        "width": "100",
                        "height": "100"
                      })
        location.icon = edited_filename

    return location


# edit location
@application.route('/location/<int:location_id>/edit', methods=['GET', 'POST'])
@login_required
def editLocation(location_id):
    editedLocation = session.query(Location).filter_by(id=location_id).one()
    if login_session['user_id'] != editedLocation.user_id:
        return redirect(url_for('showLocations'))
    if request.method == 'POST':
        if request.form['locationType'] != editedLocation.type:
            # if object change types: destroy old object, create new
            newLocation = getNewLocationTypeFromString(
                                                request.form['locationType'])
            # assign map icon to new location
            if editedLocation.icon:
                newLocation.icon = editedLocation.icon
            newLocation = addFormDataToLocation(
                                                request.form,
                                                request.files,
                                                newLocation)
            session.delete(editedLocation)
            editedLocation = newLocation
        editedLocation = addFormDataToLocation(
                                                request.form,
                                                request.files,
                                                editedLocation)
        session.add(editedLocation)
        session.commit()
        flash(editedLocation.menuLabel + " edited")
        return redirect(url_for("showLocations"))
    else:
        return render_template(
                                'editLocation.html',
                                location=editedLocation,
                                newLoc=False)


# delete location
@application.route('/location/<int:location_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteLocation(location_id):
    locationToDelete = session.query(Location).filter_by(id=location_id).one()
    if login_session['user_id'] != locationToDelete.user_id:
        return redirect(url_for('showLocations'))
    if not locationToDelete:
        return 'location not found'
    if request.method == 'POST':
        session.delete(locationToDelete)
        session.commit()
        flash(locationToDelete.menuLabel + " deleted")
        return redirect(url_for('showLocations'))
    else:
        return render_template(
                            'deletelocation.html',
                            location=locationToDelete)


def createUser(login_session):
    newUser = User(
                    name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
                                            email=login_session['email']
                                        ).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


if __name__ == '__main__':
    application.secret_key = 'super_secret_key'
    # application.debug = True
    application.run(ssl_context='adhoc')
