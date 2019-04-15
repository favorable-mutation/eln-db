#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# to run this program, use the python3 interpreter from the command line:
# python3 app.py

# then, navigate to http://127.0.0.1:5000 in a web browser

# all flask modules used by the application, available through
# pip install flask
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

# a basic MySQL connector available through
# pip install mysql-connector
import mysql.connector

# operating system tools
import os

# stop the MySQL server if it's already running, then start it
os.system("mysql.server stop")
os.system("mysql.server start")

# initialiaze the flask application
app = Flask(__name__)

# initialize global variables
err = False
u_username = False
u_password = False
cnx = False
cur = False
valid_names = []
results = []

# define behavior for root page of site
# on either GET or POST methods
@app.route("/", methods=["GET", "POST"])
def main():
    global err
    global u_username
    global u_password
    global cnx

    # if user is requesting the page, bring them to the login screen
    if request.method == "GET":
        if err:
            return render_template('index.html', name="LOTR Application", error=err)
        else:
            return render_template('index.html', name="LOTR Application")

    else:
        # collect form data for username and password on form submission
        u_username = request.form.get('user')
        u_password = request.form.get('password')

        # attempt to login to the MySQL instance with those credentials
        try:
            cnx = mysql.connector.connect(host='localhost',
                    user=u_username,
                    password=u_password,
                    database='lotrfinalrademacherg',
                    charset='utf8mb4')

            return redirect(url_for('select_char'))

        # return an error message if the MySQL server couldn't be reached or didn't
        # accept the given credentials
        except:
            err = 'Your credentials were invalid, or the MySQL server could not \
                   be reached. Please try again.'
            return redirect(url_for('main'))

# define behavior for character selection page of site
# on either GET or POST methods
@app.route("/select-character", methods=["GET","POST"])
def select_char():

    global err
    global cur
    global valid_names
    global results

    if request.method == "GET":

        valid_names = []

        cur = cnx.cursor()

        stmt_select = "select character_name from lotr_character"

        # select all character names from the database
        cur.execute(stmt_select)

        for tup in cur.fetchall():
            valid_names.append(tup[0])
        

        if err:
            return render_template('select-character.html', name="Select \
                    Character", error=err, valid_names=valid_names)
        else:
            return render_template('select-character.html', name="Select \
                    Character")

    else:
        u_char_name = request.form.get('char-name')

        if u_char_name not in valid_names:
            err = "Character not found. Please try again. \
                    Valid character names are:"
            return redirect(url_for('select_char'))

        args = [u_char_name]

        cur.callproc("track_character", args)

        output = ""
        
        results = cur.stored_results()

        # close the MySQL connection
        cur.close()
        cnx.close()

        return redirect(url_for('output'))

# define behavior for output page of site
# on either GET or POST methods
@app.route("/output")
def output():

    global results

    return render_template('output.html', name='output', output_results=results)


# if this is the main file being run, as opposed to a module called by another
# python program, run the app
if __name__ == "__main__":
    app.run()
