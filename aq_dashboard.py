"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
import openaq
import requests
from flask_sqlalchemy import SQLAlchemy

# Initialize web app
APP = Flask(__name__)

# Connect to OpenAQ API (no authentication required)
API = openaq.OpenAQ()

# Configure database to store data from OpenAQ API
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
APP.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
DB = SQLAlchemy(APP)

# Class to create Record table to store data from OpenAQ API


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'Time: {self.datetime} --- Value: {self.value}'


def get_results():

    """
    Function to return tuples of dates and mesurements of fine particulate
    matter (PM 2.5) for Los Angeles, Chile
    """
    # Obtain necessary data from OpenAQ API
    status, body = API.measurements(city='Los Angeles',
                                    parameter='pm25')

    # Convert the results from the data into a list
    results_list = list(body.values())

    tup_list = []

    # Iterate over the results list to isolate tuples ('utc_datetime','value')
    for i in range(0, len(results_list[1])):
        tup_list.append((results_list[1][i]['date']['utc'],
                         results_list[1][i]['value']))

    return tup_list


@APP.route('/')
def root():
    """Base view."""
    # Isolate records when the fine particulate matter reading was
    # equal or greater than 10
    poten_harm = Record.query.filter(Record.value >= 10).all()

    return str(poten_harm)


@APP.route('/refresh')
def refresh():

    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()

    # Get data from OpenAQ, make Record objects with it, and add to db
    updated_tup_list = get_results()

    for i in range(len(updated_tup_list)):
        new_rec = Record(id=i+1, datetime=str(updated_tup_list[i][0]),
                         value=updated_tup_list[i][1])
        DB.session.add(new_rec)

    DB.session.commit()
    return 'Data refreshed!'
