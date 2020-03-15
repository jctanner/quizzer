#!/usr/bin/env python3


import csv
import datetime
import json
import os
import random
import re
import tempfile
import uuid

from pprint import pprint
from collections import OrderedDict

from flask import Flask
from flask import redirect
from flask import render_template
from flask import send_file
from flask import request
from flask import url_for

from flaskext.markdown import Markdown
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextField

from pprint import pprint

from Levenshtein import jaro_winkler

#from lib.simpledb import SimpleDB
from lib.quizzer import Quizzer


class QuestionForm(FlaskForm):
    answer = StringField('answer')
    nextq = SubmitField(label='nextq')
    lastq = SubmitField(label='lastq')
    finished = SubmitField(label='finished')


class QuestionSearchForm(FlaskForm):
    querystring = TextField('querystring')
    submit = SubmitField(label='search')


app = Flask(__name__)
csrf = CSRFProtect(app)
Markdown(app, extensions=['tables'])
app.config['SECRET_KEY'] = '011111'
qz = Quizzer('courses')


@app.template_filter()
def is_list(var):
    """Convert a string to all caps."""
    return isinstance(var, list)


@app.template_filter()
def to_json(data):
    """ pretty printed json """
    try:
        return json.dumps(data, indent=2, sort_keys=True)
    except TypeError:
        return json.dumps(data, indent=2, sort_keys=False)


@app.route('/')
def root():
    coursenames = sorted(list(qz.courses.keys()))
    return render_template('courses.html', coursenames=coursenames)


@app.route('/images/<path:imagefile>')
def images(imagefile):
    print(imagefile)
    return send_file(imagefile, mimetype='image/png')


@app.route('/course/<coursename>', methods=['GET', 'POST'])
def course(coursename):

    searchform = QuestionSearchForm()

    if request.method == 'POST':
        qs = searchform.data['querystring']
        sessionid = qz.get_session(coursename, None, querystring=qs, count=99)
        return redirect(url_for('session', sessionid=sessionid))

    chapternames = sorted(list(qz.courses[coursename].keys()))
    chapternames = [x for x in chapternames if qz.chapter_has_questions(coursename, x)]
    report = qz.get_cached_answers_report_by_chapter(coursename=coursename)
    pprint(report)
    return render_template(
        'course.html',
        qz=qz,
        coursename=coursename,
        chapternames=chapternames,
        report=report,
        searchform=searchform
    )


@app.route('/quiz/<coursename>/<chaptername>')
@app.route('/quiz/<coursename>/<chaptername>/<int:section>')
def quiz(coursename, chaptername, section=None):
    sessionid = qz.get_session(coursename, chaptername, section=section, count=10)
    return redirect(url_for('session', sessionid=sessionid))


@app.route('/test/<coursename>/<chaptername>')
def exam(coursename, chaptername):
    sessionid = qz.get_session(coursename, chaptername, count=30)
    return redirect(url_for('session', sessionid=sessionid))


@app.route('/session/<sessionid>')
@app.route('/session/<sessionid>/<int:questionid>', methods=['GET', 'POST'])
def session(sessionid, questionid=None):
    if questionid is None:
        questionid = qz.get_next_session_qid(sessionid)
        return redirect(url_for('session', sessionid=sessionid, questionid=questionid))

    form = QuestionForm()
    question_number = qz.sessions[sessionid]['qids'].index(questionid)
    print('THIS QUESTION: %s' % question_number)

    if request.method == 'GET':
        questions_total = len(qz.sessions[sessionid]['qids'])
        question = qz.questions[questionid]
        print('# QUESTION ...')
        print(question['question'])
        print('# MARKDOWN ...')
        print(question['question_markdown'])
        random.shuffle(question['choices'])

        selected = qz.get_session_selected_answer(sessionid, questionid)

        previous_question = None
        if question_number > 0:
            previous_question = qz.sessions[sessionid]['qids'][question_number-1]
        print('LAST QUESTION: %s' % previous_question)

        next_question = None
        if (question_number + 1) < questions_total:
            next_question = qz.sessions[sessionid]['qids'][question_number]
        print('NEXT QUESTION: %s' % next_question)

        return render_template(
            'question.html',
            form=form,
            action_url=url_for('session', sessionid=sessionid, questionid=questionid),
            question=question,
            selected=selected,
            question_number=question_number + 1,
            questions_total=questions_total,
            previous_question=previous_question,
            next_question=next_question
        )

    # multiple select questions ...
    if isinstance(qz.questions[questionid]['answer'], list):
        answers = request.form.getlist('answer')
        if answers:
            qz.set_session_answer(sessionid, questionid, sorted(answers))
    else:
        print(form.data)
        answer = form.data['answer']
        print('RESPONSE: %s' % answer)
        if answer is not None and answer.strip():
            qz.set_session_answer(sessionid, questionid, answer)

    if form.data['nextq'] is True:
        r_question = qz.sessions[sessionid]['qids'][question_number+1]
        print('NEXT QUESTION: %s' % r_question)
        return redirect(url_for('session', sessionid=sessionid, questionid=r_question))
    elif form.data['lastq'] is True:
        r_question = qz.sessions[sessionid]['qids'][question_number-1]
        print('LAST QUESTION: %s' % r_question)
        return redirect(url_for('session', sessionid=sessionid, questionid=r_question))

    return redirect(url_for('report', sessionid=sessionid))


@app.route('/report/<sessionid>')
def report(sessionid):
    this_report = qz.get_session_report(sessionid)
    coursename = qz.get_session_coursename(sessionid)
    return render_template('report.html', report=this_report, coursename=coursename)


def main():
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    main()
