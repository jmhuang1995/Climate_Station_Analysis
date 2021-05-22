from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine,reflect= True)

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

app = Flask(__name__)


@app.route("/")
def welcome():
    return(f"Availiable Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>")


@app.route("/api/v1.0/precipitation")
def precipitation():
    last_point = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    year_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year, measurement.prcp != None).order_by(measurement.date).all()
    return jsonify(dict(year_prcp))


@app.route("/api/v1.0/stations")
def stations():
    session.query(measurement.station).distinct().count()
    active_stations = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    return jsonify(dict(active_stations))


@app.route("/api/v1.0/tobs")
def tobs():
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    year_temp = session.query(measurement.tobs).filter(measurement.date >= last_year, measurement.station == 'USC00519281').order_by(measurement.tobs).all()

    yer_temp = []

    for temp in year_temp:
        yer_temp.append(temp.tobs)

    return jsonify(yer_temp)

def calc_start(start):
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date >= start).all()


@app.route("/api/v1.0/<start>")
def start(start):
    calc_start_temp = calc_start(start)
    start_temp= list(np.ravel(calc_start_temp))

    start_min = start_temp[0]
    start_max = start_temp[2]
    start_avg = start_temp[1]
    start_dict = {'Min temperature': start_min, 'Max temperature':start_max, 'Avg temperature': start_avg}

    return jsonify(start_dict)

def calc_start_end(start,end):
    return session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    start_end_temp = calc_start_end(start,end)
    total_temp = list(np.ravel(start_end_temp))

    semin = total_temp[0]
    semax = total_temp[2]
    seavg = total_temp[1]
    temp_dict = {'Min temperature': semin, 'Max temperature': semax,'Avg temperature':seavg}

    return jsonify(temp_dict)



if __name__ == '__main__':
    app.run(debug=True)
