# ELN DB

## Installation

To install ELN DB, you must first install MongoDB and Python. You must also
install a few Python packages.

1. Installing MongoDB

    Refer to this helpful [guide](https://docs.mongodb.com/manual/installation/)
    to get MongoDB Server up and running on your system. The project assumes your
    mongod.conf file lives at `/usr/local/etc/mongod.conf`.

2. Configuring Admin User

    Read/write users can be configured through the frontend of the database,
    but an initial admin user must first be set up. You should follow the
    instructions at this [link](https://docs.mongodb.com/manual/tutorial/enable-authentication/),
    creating a new admin user on the `eln_db` database, instead of the `admin` database.
    Your new user should look like this:

    ```
    {
        "_id" : "eln_db.root",
        "user" : "root",
        "db" : "eln_db",
        "roles" : [
                {
                        "role" : "userAdminAnyDatabase",
                        "db" : "admin"
                },
                {
                        "role" : "readWrite",
                        "db" : "eln_db"
                }
        ],
        "mechanisms" : [
                "SCRAM-SHA-1",
                "SCRAM-SHA-256"
        ]
    }
    ```

3. Installing Python

    If you don't already have Python 3, check out this
    [link](https://www.python.org/about/gettingstarted/) for more info.

4. Installing Packages

    Run the following commands in your terminal in order to install the
    requisite `pip` packages for ELN DB:

    ```
    $ pip install flask
    $ pip install flask-pymongo
    ```

## Running the App

In order to run ELN DB, download the provided `.zip` file, and extract the
contents to a directory of your choice. It's recommended that you extract them
to a new, empty directory somewhere memorable.

Once the contents have been extracted, start the app by opening a terminal and
running the file. It will need to be given execution privileges before you can
do so (one time only), so on a Unix system, run this command in the new
directory:

```
$ chmod u+x eln_db.py
```

Once the file is executable, it can be run using the following command (again,
for Unix):

```
$ ./eln_db.py
```

## Technical Specifications

This application targets a Unix-based operating system (Linux, macOS, etc.). It
is likely possible to get it working on Windows, but auxiliary materials will
need to be consulted in terms of instructions for making the app executable and
running it on Windows.

## Schema

As a NoSQL-based application, ELN DB does not have a formal schema. It mainly
provides a frontend with some restrictions for storing user-defined data in a
MongoDB database, denoted in the following sample schema as the `user_defined`
collection. The application uses MongoDB's user management system; more information on
this can be found [here](https://docs.mongodb.com/manual/core/security-users/).

```
# Sample Schema
user = {
        _id : String,
        user : String,
        db : String,
        roles : [
                    {
                        role : String,
                        db : String
                    }
                ],
        "mechanisms" : [String]
        }

user_defined = {
                "_id" : String,
                "baz" : boolean,
                "boo" : [int],
                "notes" : int,
                "protein_yield" : String
               }
        
```

## User Flow

The following image provides a diagram of the user's journey through the
frontend of the application as a Finite State Machine:

![](eln-db-state-diagram.png)

The user can login with credentials that have access to the database `eln_db`;
if those credentials have admin access, they can use that access to create a new
read/write user, or change the password of an existing one (or their own
password). The user can, alternatively, login and view an existing dataset, or
input a new one. Along the way, their inputs are checked for validity against
the database (they cannot view a nonexistent dataset, and conversely cannot
create a new one with the same name as one that already exists). They can input
new data, view the existing data, and delete datapoints. When done, they can
simply exit the app, and kill the command-line process running it.

## Lessons Learned

As a result of this project, I have greatly developed my Flask skills, which
were previously all but nonexistent. I have identified quite a few solutions to
common problems along the way, e.g. using global variables to pass information
between different pages. I also found my way around using the Flask-PyMongo
connector, which was somewhat difficult given the semi-confusing documentation,
which requires a good understanding of the regular pymongo documentation to make
much sense. Additionally, I was able to get most of my planned features working,
but definitely could have planned my time better. I won't soon underestimate the
time required to learn new technologies again.

All code provided in this increment of the project is working as designed, and
displays errors meant to guide the user through using the application correctly.
There is some missing functionality, documented below.

## Future Work

The following features remain to be implemented for this application:

* Ability to update existing datapoints
* Ability to give new users more than read/write privileges
* Data validation to encourage users not to add values of different types for
  the same field within a dataset

The ideal usage of this database is as an Electronic Lab Notebook solution for a
research group. It falls short of being entirely usable for that because of the
missing functionality listed above, as well as the thought process for
deployment. The existing Installation Instructions only cover a local install of
the application, which would leave a database administrator for a lab with the
ugly task of figuring out how to deploy Flask on a self-hosted or cloud server
on their own. Ideally, this will be tested with different deployment strategies
in the future, and documentation will be provided for the most promising ones.
