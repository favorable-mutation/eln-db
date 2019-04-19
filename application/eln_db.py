#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# to run this program, use the python3 interpreter from the command line:
# python3 app.py

# then, navigate to http://127.0.0.1:5000 in a web browser

# all flask modules used by the application, available through
# pip install flask
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

import ast

# operating system tools
import os

# start the MongoDB server in the background
os.system("mongod --auth --config /usr/local/etc/mongod.conf &")

# initialiaze the flask application
app = Flask(__name__)

# initialize global variables
mongo = False
err = False
u_username = False
u_password = False
u_collection = False
state = False
invalid_names = []
results = []

# define behavior for login page of site
# on either GET or POST methods
@app.route("/", methods=["GET", "POST"])
def login():
    global err
    global u_username
    global u_password
    global invalid_names
    global mongo

    # if user is requesting the page, bring them to the login screen
    if request.method == "GET":
        if err:
            temp = err
            err = False
            return render_template('login.html', name="ELN DB: Login", error=err)
        else:
            return render_template('login.html', name="ELN DB: Login")

    else:
        # collect form data for username and password on form submission
        u_username = request.form.get('user')
        u_password = request.form.get('password')

        # attempt to login to the MongoDB instance with those credentials
        try:
            app.config['MONGO_AUTH_SOURCE'] = 'admin'
            app.config["MONGO_URI"] = "mongodb://" + u_username + ":" + \
                u_password +  "@localhost:27017/eln_db"
            mongo = PyMongo(app)

            return redirect(url_for('home'))

        # return an error message if the MongoDB server couldn't be reached or didn't
        # accept the given credentials
        except Exception as e:
            print(e)
            err = 'Your credentials were invalid, or the MongoDB server could not \
                   be reached. Please try again.'
            return redirect(url_for('login'))

# define behavior for login page of site
# on either GET or POST methods
@app.route("/home", methods=["GET", "POST"])
def home():

    global err
    global state

    if request.method == "GET":
        if err:
            temp = err
            err = False
            return render_template('home.html', name="ELN DB: Home", error=temp)
        else:
            return render_template('home.html', name="ELN DB: Home")

    else:
        if 'view' in request.form:
            state = "What dataset would you like to view?"
            return redirect(url_for('lookup'))
        elif 'input' in request.form:
            state = "What would you like to call your dataset?"
            return redirect(url_for('lookup'))
        else:
            return render_template('home.html', name="ELN DB: Home")

# define behavior for dataset lookup/creation page of site
# on either GET or POST methods
@app.route("/lookup", methods=["GET","POST"])
def lookup():

    global err
    global state
    global invalid_names
    global u_collection
    global results

    if request.method == "GET":

        invalid_names = mongo.db.list_collection_names()

        if err:
            temp = err
            err = False
            return render_template('lookup.html', name="ELN DB: \
                    Lookup", state=state, \
                    error=temp, invalid_names=invalid_names)
        else:
            return render_template('lookup.html', name="ELN DB: \
                    Lookup", state=state)

    else:
        u_collection = request.form.get('lookup')

        if u_collection in invalid_names and state == "What would you like to call your dataset?":
            err = "Dataset already exists. Please try again. \
                    Existing dataset names are:"
            return redirect(url_for('lookup'))

        elif u_collection in invalid_names:
            return redirect(url_for('view'))

        elif state == "What dataset would you like to view?":
            err = "Dataset not found. Please try again. \
                    Existing dataset names are:"
            return redirect(url_for('lookup'))

        elif u_collection not in invalid_names:
            return redirect(url_for('edit'))

        else:
            return redirect(url_for('login'))

# define behavior for data view page of site
# on either GET or POST methods
@app.route("/view", methods=["GET","POST"])
def view():

    global results

    if request.method == "GET":
        mongo_collection = mongo.db[u_collection]
        results = mongo_collection.find()
        return render_template('view.html', name='ELN DB: View Data',
                view_results=results, dataset=u_collection)
    elif 'edit' in request.form:
        return redirect(url_for('edit'))
    else:
        return redirect(url_for('home'))

# define behavior for data editing page of site
# on either GET or POST methods
@app.route("/edit", methods=["GET","POST"])
def edit():

    global results
    global err

    if request.method == "GET":
        mongo_collection = mongo.db[u_collection]
        results = mongo_collection.find()
        if err:
            return render_template('edit.html', name='ELN DB: Edit Data',
                    view_results=results, dataset=u_collection, error=err)
        else:
            return render_template('edit.html', name='ELN DB: Edit Data',
                    view_results=results, dataset=u_collection)

    elif 'cancel' in request.form:
        return redirect(url_for('home'))
    else:
        try:
            mongo_collection = mongo.db[u_collection]
            data = request.form.get('data')
            mongo_collection.insert_one(ast.literal_eval(data))
            return redirect(url_for('view'))

        # return an error message if the MongoDB server couldn't be reached or didn't
        # accept the given credentials
        except Exception as e:
            print(e)
            err = 'Please enter a valid data format.'
            return redirect(url_for('edit'))

# if this is the main file being run, as opposed to a module called by another
# python program, run the app
if __name__ == "__main__":
    app.run()
