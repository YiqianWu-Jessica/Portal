#!/usr/local/bin/python3
import sqlite3
# we are adding the import 'g' which will be used for the database
from flask import Flask, session, redirect, url_for, escape,  request, render_template, g
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask.helpers import flash

app = Flask(__name__)
app.secret_key=b'abbas'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
db = SQLAlchemy(app)

@app.route('/')
def index():
	# if user logged in, then send to index according to usertype
	if 'username' in session:
		row = "select username, usertype from users where username == '{}'".format(session['username'])
		result = db.engine.execute(text(row))
		for user in result:
			if user['usertype'] == 'instructor':
				return render_template('instructor_index.html')
			elif user['usertype'] == 'student':
				return render_template('student_index.html')
	else:
		# other wise send to login
		return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	# fetch username and password, then authenticate by fetching data from database
	if request.method == 'POST':
		name_input = request.form['username']
		password_input = request.form['password']
		users = db.engine.execute(text("select * from users"))
		for user in users:
			if user['username'] == name_input:
				if user['password'] == password_input:
					# if authenticated then direct to index by usertype
					session['username'] = name_input
					return redirect(url_for('index'))	
		return render_template('login.html', login=False)
	else:
		return render_template('login.html')
            
@app.route('/register',methods=['GET','POST'])
def register():
	# check the user name
    if 'username' in session:
        return redirect(url_for('logout'))
	# register a new user into the database
    if request.method =='POST':
        usertype = request.form['type']
        username = request.form['username']
        password = request.form['password']
        user_old = db.engine.execute(text("select * from users"))
        for user in user_old:
            if user["username"] == username:
                return render_template("register.html")
        newuser =  "insert into users (username, password, usertype) values ('{}', '{}', '{}')".format(username, password, usertype)
        db.engine.execute(text(newuser))
    return render_template('register.html')

@app.route('/logout')
def logout():
	# take user out of session then direct to login
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/instructor_anonfeedback', methods=['POST', 'GET'])
def instructor_anonfeedback():
	# check the user name
	if 'username' not in session:
		return redirect(url_for('instructor_anonfeedback '))
	# enter into this user's text file of database to find the user's type
	feedbackQuery = "select feedback from instructor_feedback where username == '{}'".format(session['username'])
	feedback = db.engine.execute(text(feedbackQuery))
	# for loop the types and get the matches file
	return render_template('instructor_anonfeedback.html', feedbacks=feedback)

@app.route('/student_anonfeedback', methods=['POST', 'GET'])
def student_anonfeedback():
		# check the user name
	if 'username' not in session:
		return redirect(url_for('instructor_anonfeedback '))
	# fetch feedback from student then send to database
	feedbackQuery = "select feedback from student_feedback where username == '{}'".format(session['username'])
	feedback = db.engine.execute(text(feedbackQuery))
	return render_template('student_anonfeedback.html', feedbacks=feedback)

@app.route('/instructor_feedback', methods=['POST', 'GET'])
def instructor_feedback():
	if 'username' not in session:
		return redirect(url_for('instructor_anonfeedback'))
	# instructor changes feedback for student if feedback already exists, or 
    # adds one if there arent any
	if request.method =='POST':
		student_name = request.form['student_name']
		r1 = request.form['feedback_name']
		r = session['username'] + ': ' + r1
		#user_old = db.engine.execute(text("select username from student_feedback"))
		#for student_name in user_old:
			#insertSQL = "update student_feedback set feedback='{}' where username == '{}'".format(r,student_name)
		insertSQL = "insert into student_feedback(username, feedback) values ('{}', '{}')".format( student_name, r)
		db.engine.execute(text(insertSQL))
	return render_template('instructor_feedback.html')

@app.route('/student_feedback', methods=['POST', 'GET'])
def student_feedback():
	if 'username' not in session:
		return redirect(url_for('student_anonfeedback'))
	# fetches feedback from html then send to database for instructors
	if request.method =='POST':
		instructor_name = request.form['instructor_name']
		r1 = request.form['fname1']
		r2 = request.form['fname2']
		r3 = request.form['fname3']
		r4 = request.form['fname4']
		r5 = request.form['fname5']
		r = session['username'] + ': ' + r1 +', ' + r2 +', ' + r3 + ', '+ r4 + ', '+ r5
		#user_old = db.engine.execute(text("select username from instructor_feedback"))
		#if instructor_name in user_old:
		#	insertSQL = "update instructor_feedback set username='{}' and feedback='{}' ".format( instructor_name, r)
		#else:
		#	insertSQL = "insert into instructor_feedback(username, feedback) values ('{}', '{}')".format( instructor_name, r)
		insertSQL = "insert into instructor_feedback(username, feedback) values ('{}', '{}')".format( instructor_name, r)
		db.engine.execute(text(insertSQL))
	return render_template('student_feedback.html')

@app.route('/instructor_mark', methods=['GET', 'POST'])
def instructor_mark():
	if 'username' not in session:
		return redirect(url_for('instructor_mark'))
	marks = "select * from grade"
	result = db.engine.execute(text(marks))
	return render_template('instructor_mark.html', grades=result)

@app.route('/student_mark', methods=['POST', 'GET'])
def student_mark():
	if 'username' not in session:
		return redirect(url_for('student_mark'))
	# fetch marks for student and pass to html to display
	mark = "select * from grade where username == '{}'".format(session['username'])
	student_mark = db.engine.execute(text(mark))
	return render_template('student_mark.html', grade=student_mark)

@app.route('/instructor_remark', methods=['POST', 'GET'])
def instructor_remark():
    if 'username' not in session:
        return redirect(url_for('instructor_mark'))
    # changes mark for a student, changes data in the database
    if request.method =='POST':
        name = request.form['remark_student']
        subject = request.form['remark_subject']
        new_grade = request.form['remark_grade']
        if subject == "":
            return render_template('instructor_remark.html', requests=None)
        insertSQL = "UPDATE grade SET '{}'='{}' WHERE username == '{}'".format(subject, new_grade, name)
        db.engine.execute(text(insertSQL))
	# displays all remark requests
    remarks = "select * from remark_requests"
    result = db.engine.execute(text(remarks))
    return render_template('instructor_remark.html', requests=result)

@app.route('/student_remark', methods=['POST', 'GET'])
def student_remark():
	if 'username' not in session:
		return redirect(url_for('student_mark'))
	# submit remark request to database where it could be send to instructors
	if request.method =='POST':
		name = session['username']
		remark_subject = request.form['remark_subject']
		r = request.form['remark_request']
		insertSQL = "insert into remark_requests(username,subject,reason) values ('{}', '{}', '{}')".format(name,remark_subject, r)
		db.engine.execute(text(insertSQL))
	return render_template('student_remark.html')

@app.route('/instructor_Slides', methods=['POST', 'GET'])
def instructor_Slides():
	return render_template('instructor_Slides.html')

@app.route('/student_Slides', methods=['POST', 'GET'])
def student_Slides():
	return render_template('student_Slides.html')

@app.route('/instructor_assignment', methods=['POST', 'GET'])
def instructor_assignment():
	return render_template('instructor_assignment.html')

@app.route('/student_assignment', methods=['POST', 'GET'])
def student_assignment():
	return render_template('student_assignment.html')

@app.route('/instructor_lab', methods=['POST', 'GET'])
def instructor_lab():
	return render_template('instructor_lab.html')

@app.route('/student_lab', methods=['POST', 'GET'])
def student_lab():
	return render_template('student_lab.html')

@app.route('/instructor_test', methods=['POST', 'GET'])
def instructor_test():
	return render_template('instructor_test.html')

@app.route('/student_test', methods=['POST', 'GET'])
def student_test():
	return render_template('student_test.html')

@app.route('/instructor_calendar', methods=['POST', 'GET'])
def instructor_calendar():
	return render_template('instructor_calendar.html')

@app.route('/student_calendar', methods=['POST', 'GET'])
def student_calendar():
	return render_template('student_calendar.html')

@app.route('/instructor_courseteam', methods=['POST', 'GET'])
def instructor_courseteam():
	return render_template('instructor_courseteam.html')

@app.route('/student_courseteam', methods=['POST', 'GET'])
def student_courseteam():
	return render_template('student_courseteam.html')


@app.route('/instructor_index', methods=['POST', 'GET'])
def instructor_index():
	return render_template('instructor_index.html')

@app.route('/student_index', methods=['POST', 'GET'])
def student_index():
	return render_template('student_index.html')

if __name__=="__main__":
	#app.run(host='0.0.0.0', port=5000, debug=True)
	app.run(debug=True)

