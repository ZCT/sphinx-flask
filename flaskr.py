import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.paginate import Pagination
#from
from contextlib import closing
from search import sphinx_search

PROJECT_DIR = os.getcwd()

#configuration
DATABASE = PROJECT_DIR + '/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
RESULTS_PER_PAGE = 10

#create our app
app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


@app.route('/show')
def show_entries():
    keyword = request.form['Text']
    entries = dict(title=keyword, text=keyword)
    return render_template('show_entries.html', entries=entries)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged_in')
            return render_template('show_entries.html', show_result=False)
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/result',methods=['GET'])
def showresult(entries):
    try:
        page=int(request.args.get('page',1))
    except ValueError:
        page=1
    pagination=Pagination(page=page, total=len(entries), search=False, css_framework='foundation')
    return render_template('show_entries.html', entries=entries, pagination=pagination,show_result=True)

entries=[]

def get_entry_for_page(page,length,entries):
    entry_page=[]
    for i in range(10):
        index= page*10-10+i
        if index < len(entries):
            entry_page.append(entries[index])
    return entry_page

@app.route('/search', methods=['GET','POST'])
def search():
    global entries
    page=1
    if not session.get('logged_in'):
        abort(401)
    if request.method=='POST':
        entries=[]
        flash('The matched result is:')
        keyword = request.form['Text']
        entries = sphinx_search(keyword)
    else:
        try:
            page=int(request.args.get('page',1))
        except ValueError:
            page=1
    page_entries=get_entry_for_page(page,10,entries)
    pagination=Pagination(page=page, total=len(entries), search=False, record_name='result')
    return render_template('show_entries.html', entries=page_entries, pagination=pagination,show_result=True)






@app.route('/download')
def download():
    return redirect(url_for('static', filename='flaskr.db'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(host='0.0.0.0', port=port)
