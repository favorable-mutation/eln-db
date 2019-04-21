#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# to run this program, use the python3 interpreter from the command line:
# python3 eln_db.py

# then, navigate to http://127.0.0.1:5000 in a web browser

# requires a user on the database eln_db - use that username and password to
# login - unauthenticated access is not supported, as is deployment on server

# dependencies: install mongodb, as well as python3, all pip packages
# setup access control on mongodb with an admin user on the eln_db database
# new user page will prompt you for the admin creds
# extract zip into folder, run with ./eln_db.py


# all flask modules used by the application, available through:
# pip install flask
from flask import Flask, render_template, request, redirect, send_file, url_for

# import MongoDB connector, installed with:
# pip install flask-pymongo
from flask_pymongo import PyMongo

# get ObjectIds
import pymongo
from bson.objectid import ObjectId

# import dict-parsing tools
import ast

# operating system tools
import os

# current time for labelling data exports
import datetime

# regexes for validating collection names, etc
import re


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
field_set = set()
u_fields = set()


# define behavior for login page of site on either GET or POST methods
@app.route("/", methods=["GET", "POST"])
def login():

    global mongo
    global err
    global u_username
    global u_password
    global invalid_names

    # if user is requesting the page, bring them to the login screen
    if request.method == "GET":

        # display an error message, if there is one set
        if err:

            temp = err
            err = False

            return render_template(
                "login.html", name="ELN DB: Login", error=temp
            )

        else:

            return render_template("login.html", name="ELN DB: Login")

    else:

        # collect form data for username and password
        u_username = request.form.get("user")
        u_password = request.form.get("password")

        try:

            # attempt to login to the MongoDB instance with those credentials
            app.config["MONGO_URI"] = (
                "mongodb://"
                + u_username
                + ":"
                + u_password
                + "@localhost:27017/eln_db"
            )
            mongo = PyMongo(app)

            # get a list of all collection names in the database
            invalid_names = mongo.db.list_collection_names()

            # if user clicks the submit button
            if "submit" in request.form:
                return redirect(url_for("home"))

            # if user clicks the new user button
            elif "manage" in request.form:
                return redirect(url_for("admin"))

        # return an error message if the MongoDB server couldn't be reached or
        # didn't accept the given credentials
        except Exception as e:

            print(e)
            err = "Your credentials were invalid, or the MongoDB server could \
                    not be reached. Please try again."

            return redirect(url_for("login"))


# define behavior for admin page of site on either GET or POST methods
@app.route("/admin", methods=["GET", "POST"])
def admin():

    global mongo
    global err
    global u_username
    global u_password

    # if user is requesting the page, bring them to the login screen
    if request.method == "GET":

        return render_template("admin.html", name="ELN DB: Admin")

    # if the user clicks the submit button
    elif "submit" in request.form:

        # collect form data for username and password
        u_username = request.form.get("user")
        u_password = request.form.get("password")

        try:

            # get the users on eln_db with the given username
            u_users = mongo.db.command("usersInfo", u_username)

            # if there is already a user with that username
            if u_users["users"]:

                # update their password
                mongo.db.command("updateUser", u_username, pwd=u_password)

            else:

                # add a new user with the given username and password and readWrite
                # access on the database
                # NOTE: creating admins through the webapp and read-only users are
                # unsupported
                mongo.db.command(
                    "createUser",
                    u_username,
                    pwd=u_password,
                    roles=["readWrite"],
                )

        # return an error message if the MongoDB server couldn't be reached or
        # didn't accept the given credentials
        except Exception as e:

            print(e)
            err = "Your credentials were invalid, or you are not an admin on \
            the MongoDB server. Please try again."

        return redirect(url_for("login"))


# define behavior for login page of site on either GET or POST methods
@app.route("/home", methods=["GET", "POST"])
def home():

    global err
    global state

    # if user is requesting the page, bring them to the homepage
    if request.method == "GET":

        # display an error message, if there is one set
        if err:

            temp = err
            err = False

            return render_template("home.html", name="ELN DB: Home", error=temp)

        else:

            return render_template("home.html", name="ELN DB: Home")

    # if the button choice is viewing a dataset
    elif "view" in request.form:

        state = "What dataset would you like to view?"

        return redirect(url_for("lookup"))

    # if the button choice is inputting a dataset
    elif "input" in request.form:

        state = "What would you like to call your dataset?"

        return redirect(url_for("lookup"))


# define behavior for dataset lookup/creation page of site on either GET or
# POST methods
@app.route("/lookup", methods=["GET", "POST"])
def lookup():

    global err
    global u_collection
    global state
    global invalid_names

    # if user is requesting the page, bring them to the dataset lookup page
    if request.method == "GET":

        # display an error message, if there is one set
        if err:

            temp = err
            err = False

            return render_template(
                "lookup.html",
                name="ELN DB: Lookup",
                state=state,
                error=temp,
                invalid_names=invalid_names,
            )

        else:

            return render_template(
                "lookup.html", name="ELN DB: Lookup", state=state
            )

    # if user clicks the submit button
    elif "submit" in request.form:

        try:

            # collect form data for collection to fetch
            u_collection = request.form.get("lookup")

            # if the user is trying to input data
            if state == "What would you like to call your dataset?":

                # if the collection exists
                if u_collection in invalid_names:

                    # throw an error telling them what collections already exist
                    err = "Dataset already exists. Please try again. \
                            Existing dataset names are:"

                    return redirect(url_for("lookup"))

                # if the collection name doesn't match the right pattern
                elif not re.fullmatch("[a-zA-Z0-9_]*", u_collection):

                    # throw an error telling them what collections already exist
                    err = "Dataset names cannot contain special characters. \
                            Please use underscores (_) as separators, and \
                            try again. Existing dataset names are:"

                    return redirect(url_for("lookup"))

                # if the user is creating a collection with a valid name
                else:

                    # take them to the input page
                    return redirect(url_for("edit"))

            # if the user is trying to view a collection
            elif state == "What dataset would you like to view?":

                # if the collection exists
                if u_collection in invalid_names:

                    # send them to view it
                    return redirect(url_for("view"))

                # if the collection does not exist
                else:

                    # throw an error telling them what collections already exist
                    err = "Dataset not found. Please try again. \
                            Existing dataset names are:"

                    return redirect(url_for("lookup"))

        # if the user has reached this page without going through the homepage
        except Exception as e:

            print(e)
            err = "Your credentials were invalid, or you do not have the \
            necessary permissions to access this dataset. Please try again."

            # send them back to the login page
            return redirect(url_for("login"))

    # if the user clicks the cancel button
    elif "back" in request.form:

        # take them back to the homepage
        return redirect(url_for("home"))


# define behavior for data view page of site on either GET or POST methods
@app.route("/view", methods=["GET", "POST"])
def view():

    global mongo
    global err
    global u_username
    global u_password
    global u_collection
    global results
    global field_set
    global u_fields

    # if user is requesting the page
    if request.method == "GET":

        try:

            # initialize empty set and get iterable collection from MongoDB
            mongo_collection = mongo.db[u_collection]
            cur = mongo_collection.find()
            field_set = set()
            results = []

            # iterate through collection and add each key of each dict object in
            # collection to set to produce list of unique field names
            for result in cur:
                results.append(result)
                field_set.update(list(result))

            # close the cursor
            cur.close()

            return render_template(
                "view.html",
                name="ELN DB: View Data",
                view_results=results,
                dataset=u_collection,
            )

        # if the user has reached this page without going through the homepage
        except Exception as e:

            print(e)
            err = "Your credentials were invalid, or you do not have the \
            necessary permissions to access this dataset. Please try again."

            # send them back to the login page
            return redirect(url_for("login"))

    # if the user clicks the edit button
    elif "edit" in request.form:

        # take them to the edit page
        return redirect(url_for("edit"))

    # if the user clicks the export button
    elif "export" in request.form:

        # collect form data for fields to export
        u_fields = set(request.form.get("fields").split(","))

        u_fields = u_fields.intersection(field_set)

        if not u_fields:
            u_fields = field_set

        try:

            # build a path for the export file
            path = "static/export/export-"
            path += u_collection
            path += "-"

            # print datetime in format "Dec-31-99-2359"
            path += datetime.datetime.now().strftime("%b-%d-%y-%H%M")
            path += ".csv"

            # remove the _id field
            u_fields.remove("_id")

            # place the _id field first in the fields to output, then add the
            # rest in alphabetical order to a comma-delimited list
            fields = "_id,"
            fields += ",".join(sorted(u_fields))

            # export the .csv
            os.system(
                "mongoexport --username "
                + u_username
                + " "
                + "--password "
                + u_password
                + " "
                + "--db eln_db "
                + "--collection "
                + u_collection
                + " "
                + "--type=csv "
                + "--fields "
                + fields
                + " "
                + "--out ./"
                + path
            )

            return send_file(path, as_attachment=True)

        # if the user has reached this page without going through the homepage
        except Exception as e:

            print(e)
            err = "Your credentials were invalid, or you do not have the \
            necessary permissions to access this dataset. Please try again."

            # send them back to the login page
            return redirect(url_for("login"))

    # if the user clicks the back button
    elif "back" in request.form:

        # take them back to the homepage
        return redirect(url_for("home"))


# define behavior for data editing page of site on either GET or POST methods
@app.route("/edit", methods=["GET", "POST"])
def edit():

    global mongo
    global err
    global u_collection
    global results
    global field_set
    global u_fields

    # if user is requesting the page
    if request.method == "GET":

        try:

            # initialize empty set and get iterable collection from MongoDB
            mongo_collection = mongo.db[u_collection]
            cur = mongo_collection.find()
            field_set = set()
            results = []

            # iterate through collection and add each key of each dict object in
            # collection to set to produce list of unique field names
            for result in cur:
                results.append(result)
                field_set.update(list(result))

            # close the cursor
            cur.close()

            if not u_fields:
                u_fields = field_set

            u_fields.add("_id")

            fields = sorted(u_fields)

            # display an error message, if there is one set
            if err:

                return render_template(
                    "edit.html",
                    name="ELN DB: Edit Data",
                    view_results=results,
                    dataset=u_collection,
                    fields=fields,
                    error=err,
                )

            else:

                return render_template(
                    "edit.html",
                    name="ELN DB: Edit Data",
                    view_results=results,
                    fields=fields,
                    dataset=u_collection,
                )

        # if the user has reached this page without going through the homepage
        except Exception as e:

            print(e)
            err = "Your credentials were invalid, or you do not have the \
            necessary permissions to access this dataset. Please try again."

            # send them back to the login page
            return redirect(url_for("login"))

    # if the user clicks the set-fields button
    elif "set-fields" in request.form:

        fields = request.form.get("fields")

        # if the field names don't match the right pattern
        if not re.fullmatch("[a-zA-Z0-9_,]*", fields):

            # throw an error telling them what collections already exist
            err = "Field names cannot contain special characters. \
                    Please use underscores (_) as word separators within field \
                    names, and try again."

            return redirect(url_for("edit"))

        u_fields = set(fields.split(","))

        return redirect(url_for("edit"))

    # if the user clicks the cancel button
    elif "cancel" in request.form:

        # take them back to the homepage
        return redirect(url_for("home"))

    # if the user clicks the save button
    elif "save" in request.form:

        try:

            # TODO data validation as necessary
            # if a field already has a value, the input value should be the same
            # type to ensure integrity for later data analysis - this limits the
            # abilities of a NoSQL database but encourages good data collection
            # practices for science

            new_val = "{"

            for field in sorted(u_fields):
                value = request.form.get(field)
                if not value == "":
                    if not new_val == "{":
                        new_val += ", "
                    new_val += "'"
                    new_val += field
                    new_val += "': "
                    # NOTE: Strings must contain only alphabetic
                    # characters and _
                    if re.fullmatch("[a-zA-Z_]*", value):
                        new_val += "'"
                        new_val += value
                        new_val += "'"
                    else:
                        new_val += value

            new_val += "}"

            print(new_val)

            new_val = ast.literal_eval(new_val)

            print(type(new_val))

            # get the data the user has entered and put it into the collection
            mongo_collection = mongo.db[u_collection]
            mongo_collection.insert_one(new_val)

            return redirect(url_for("edit"))

        # return an error message if the user didn't enter valid data
        except Exception as e:

            print(e)
            err = "Please enter a valid data format."

            return redirect(url_for("edit"))

    elif "remove" in request.form:

        # get the id of the document to remove and remove it, trying both
        # ObjectIds and regular String ids
        rm_id = request.form.get("remove")
        mongo_collection = mongo.db[u_collection]

        try:
            mongo_collection.delete_one({"_id": ObjectId(rm_id)})
        except Exception as a:
            print(a)

        mongo_collection.delete_one({"_id": rm_id})

        # take them back to the homepage
        return redirect(url_for("edit"))


# if this is the main file being run, as opposed to a module called by another
# python program, run the app
if __name__ == "__main__":

    app.run()
