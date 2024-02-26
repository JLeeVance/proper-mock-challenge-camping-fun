#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

class Index(Resource):

    def get(self):
        return make_response('<h1>Home</h1>', 200)

api.add_resource(Index, '/')

class Campers(Resource):

    def get(self):
        campers = [camper.to_dict() for camper in Camper.query.all()]
        return make_response(campers, 200)
    
    def post(self):
        try:
            post_data = request.get_json()
            new_camper = Camper()

            for key, value in post_data.items():
                setattr(new_camper, key, value)
            
            db.session.add(new_camper)
            db.session.commit()

            return make_response(new_camper.to_dict(), 202)
        except:
            return make_response({'errors': ['validation errors']}, 400)

api.add_resource(Campers, '/campers')

class CamperById(Resource):

    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if not camper:
            return make_response({'error':'Camper not found'}, 404)
        
        return make_response(camper.to_dict(rules=('signups', '-signups.camper')), 200)
    
    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if not camper:
            return make_response({'error':'Camper not found'}, 404)
        
        try:
            patch_data = request.get_json()
        
            for key, value in patch_data.items():
                setattr(camper, key, value)
            
            db.session.commit()

            return make_response(camper.to_dict(), 202)
        except:
            return make_response({'errors':['validation errors']}, 400)      

api.add_resource(CamperById, '/campers/<int:id>')

class Activities(Resource):

    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all()]
        return make_response(activities, 200)

api.add_resource(Activities, '/activities')

class ActivityByID(Resource):

    def get(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if not activity:
            return make_response({'error':'Activity not found'}, 404)
        
        return make_response(activity.to_dict(), 200)
    
    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if not activity:
            return make_response({'error':'Activity not found'}, 404)
        
        db.session.delete(activity)
        db.session.commit()

        return make_response({}, 204)

api.add_resource(ActivityByID, '/activities/<int:id>')

class Signups(Resource):

    def get(self):
        signups = [signup.to_dict() for signup in Signup.query.all()]
        if not signups:
            return make_response({'error':'No signups found'}, 404)
        
        return make_response(signups, 200)
    
    def post(self):
        post_data = request.get_json()
        new_signup = Signup()
        try:
            for key, value in post_data.items():
                setattr(new_signup, key, value)
            
            db.session.add(new_signup)
            db.session.commit()

            return make_response(new_signup.to_dict(), 201)
        except:
            return make_response({'errors': ['validation errors']}, 400)

api.add_resource(Signups, '/signups')
        

    




# @app.route('/')
# def home():
#     return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
