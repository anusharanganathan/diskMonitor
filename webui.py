# -*- coding: utf-8 -*-
"""
    Disk monitor

    An example application written using Flask and sqlite3. 
    The monitoring of files is done using Celery.

    Copyright: (c) 2012 by Anusha Ranganathan.
"""
from __future__ import with_statement
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack,  make_response
from diskMonitorConfig import DATABASE, TABLE
from conneg import MimeType as MT, parse as conneg_parse
from dbHandler import dbHandler
import json

# configuration
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
db = dbHandler(database=DATABASE, table=TABLE)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

"""
def init_db():
    "Creates the database tables."
    with app.app_context():
        top = _app_ctx_stack.top
        if not hasattr(top, 'sqlite_db'):
            top.sqlite_db = dbHandler(database=DATABASE, table=TABLE)
"""
def get_db():
    "Opens a new database connection if there is none yet for the current application context."
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = dbHandler(database=DATABASE, table=TABLE)
    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    "Closes the database again at the end of the request."
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

@app.route('/files', methods=['GET'])
def files():
    if request.method == 'GET':
        format = request.args.get('format', '')
        accept_list= None
        if format:
            if format == "html":
                accept_list= [MT("text", "html")]
            elif format == "json":
                accept_list= [MT("application", "json")]
        start = request.args.get('start', '')
        rows = request.args.get('rows', '')
        get_db()
        top = _app_ctx_stack.top
        ans = top.sqlite_db.getRecords(start=start, rows=rows)

        #db.getRecords(start=start, rows=rows)
        print dir(request)
        if not accept_list and request.accept_mimetypes:
            try:
                accept_list = conneg_parse(request.accept_mimetypes)
            except:
                accept_list= [MT("text", "html")]

        if not accept_list:
            accept_list= [MT("application", "json")]

        mimetype = accept_list.pop(0)        
        while(mimetype):
            if str(mimetype).lower() in ["text/html", "text/xhtml"]:
                return render_template('show_files.html', files=ans)
            elif str(mimetype).lower() in ["text/plain", "application/json"]:
                resp = make_response(json.dumps(ans), 200)
                resp.headers['Content-Type'] = 'application/json; charset="UTF-8"'
                return resp
            try:
                mimetype = accept_list.pop(0)
            except IndexError:
                mimetype = None
        #Whoops nothing satisfies - return application/json
        resp = make_response(json.dumps(files), 200)
        resp.headers['Content-Type'] = 'application/json; charset="UTF-8"'
        return resp

@app.route('/file', methods=['GET'])
def each_file():
    if request.method == 'GET':
        format = request.args.get('format', '')
        filepath = request.args.get('path', '')
        accept_list= None
        if format:
            if format == "html":
                accept_list= [MT("text", "html")]
            elif format == "json":
                accept_list= [MT("application", "json")]
        get_db()
        top = _app_ctx_stack.top
        ans = top.sqlite_db.getRecord(filepath)

        #db.getRecords(start=start, rows=rows)
        if not accept_list and request.accept_mimetypes:
            try:
                accept_list = conneg_parse(request.accept_mimetypes)
            except:
                accept_list= [MT("text", "html")]

        if not accept_list:
            accept_list= [MT("application", "json")]

        mimetype = accept_list.pop(0)        
        while(mimetype):
            if str(mimetype).lower() in ["text/html", "text/xhtml"]:
                return render_template('each_file.html', files=ans)
            elif str(mimetype).lower() in ["text/plain", "application/json"]:
                resp = make_response(json.dumps(ans), 200)
                resp.headers['Content-Type'] = 'application/json; charset="UTF-8"'
                return resp
            try:
                mimetype = accept_list.pop(0)
            except IndexError:
                mimetype = None
        #Whoops nothing satisfies - return application/json
        resp = make_response(json.dumps(files), 200)
        resp.headers['Content-Type'] = 'application/json; charset="UTF-8"'
        return resp

if __name__ == '__main__':
    #init_db()
    app.run()
