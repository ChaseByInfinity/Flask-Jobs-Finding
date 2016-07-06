import os
from flask import Flask, render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import sha256_crypt
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import gc
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/jobs'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.Unicode)
    email = db.Column('email', db.Unicode)
    password = db.Column('password', db.Unicode)
    
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        
class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column('id', db.Integer, primary_key=True)
    job_name = db.Column('job_name', db.Unicode)
    job_poster = db.Column('job_poster', db.Unicode)
    job_posted = db.Column('job_posted', db.DateTime)
    category = db.Column('category', db.Unicode)
    job_desc = db.Column('job_desc', db.Unicode)
    fulfilled = db.Column('fulfilled', db.Boolean)
    
    
    def __init__(self, job_name, job_poster, job_posted, category, job_desc, fulfilled):
        self.job_name = job_name
        self.job_poster = job_poster
        self.job_posted = job_posted
        self.category = category
        self.job_desc = job_desc
        self.fulfilled = fulfilled


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column('id', db.Integer, primary_key=True)
    cat_name = db.Column('cat_name', db.Unicode)
    
    def __init__(self, cat_name):
        self.cat_name = cat_name
        
        
class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column('id', db.Integer, primary_key=True)
    applicant = db.Column('applicant', db.Unicode)
    message = db.Column('message', db.Unicode)
    date_applied = db.Column('date_applied', db.Unicode)
    for_listing = db.Column('for_listing', db.Integer)
    
    
    def __init__(self, applicant, message, date_applied, for_listing):
        self.applicant = applicant
        self.message = message
        self.date_applied = date_applied
        self.for_listing = for_listing

        
        
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap

import jobs.views