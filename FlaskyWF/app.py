# coding: utf-8

from __future__ import unicode_literals
import support
import time
import flask_wtf
from wtforms import *
from flask import Flask, jsonify, request, redirect, url_for
from flask import render_template, current_app, session
from flask_bootstrap import Bootstrap
from flask_paginate import get_page_parameter, get_page_args
from wtforms.fields.html5 import DateField
from wtforms.fields import SelectField
from flask.ext.ypaginate import Pagination
from flask_script import Manager

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
bootstrap = Bootstrap(app)
manager = Manager(app)


class TimeRangeForm(flask_wtf.FlaskForm):
    dt_from = DateField('From',
                        format='%Y-%m-%d',
                        validators=[validators.Optional(), ])
    dt_to = DateField('To',
                      format='%Y-%m-%d',
                      validators=[validators.Optional(), ])


class PopularForm(TimeRangeForm):
    target = SelectField(u"目标",
                         default=0,
                         choices=[(0, u'关键词'),
                                  (1, u'作者')],
                         coerce=int)
    classes = list(support.get_all_main_class())
    class_ids = [i[1] for i in classes]

    major = SelectField(u"分类",
                        default=8,
                        choices=[(idx, unicode(elem[0])) for idx, elem in enumerate(classes)]
                                + [(8, u'所有分类')],
                        coerce=int,
                        validators=[validators.Optional(), ])
    submit = SubmitField('GENERATE')


class SearchForm(flask_wtf.FlaskForm):
    range_limit = RadioField('range_limit',
                             choices=[('title', u'标题'),
                                      ('author', u'作者'),
                                      ('abstract', u'摘要'),
                                      # ('ol_publish_time', u'时间'),
                                      ("fulltext", u"全文搜索")],
                             default='title')
    search_words = StringField("",
                               validators=[validators.InputRequired()],
                               render_kw={"placeholder": u"输入搜索内容"})
    submit = SubmitField('SEARCH')


@app.route('/', methods=['GET', "POST"])
def index():
    form = SearchForm()
    a = request
    if request.method == "POST":
        if form.validate_on_submit():
            return redirect(url_for('search_result',
                                    search_words=form.search_words.data,
                                    range_limit=form.range_limit.data))
    return render_template('index.html', form=form)


@app.route('/search_result', methods=["GET", "POST"])
def search_result():
    # req = request
    range_limit = request.args['range_limit']
    search_words = request.args['search_words']

    page, per_page, offset = get_page_args()
    db_results = support.search(range_limit,
                                search_words)
    results = db_results[0]
    counts = int(db_results[1])
    pagination = Pagination(page=page,
                            total=counts,
                            search=True,
                            record_name='users',
                            css_framework=get_css_framework(),
                            outerWindow=1,
                            ecord_name="results",
                            format_total=True,
                            format_number=True,
                            per_page=per_page
                            )
    return render_template('search_result.html',
                           search_words=search_words,
                           results=results.skip(offset).limit(per_page),
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           active_url='users-page-url',
                           form=form)


@app.route('/item/')
def item():
    item = support.get_by_id(request.args['obj_id'])
    return render_template("item.html",
                           item=item)


@app.route('/popular', methods=['POST', 'GET'])
def popular():
    form = PopularForm()
    if request.method == "POST":
        if form.validate_on_submit():
            target = form.target.data
            _from = time.mktime(form.dt_from.data.timetuple()) if form.dt_from.data else form.dt_from.data
            _to = time.mktime(form.dt_to.data.timetuple()) if form.dt_to.data else form.dt_to.data
            class_id = form.class_ids[form.major.data] if form.major.data != 8 else None
            top100 = support.get_popular_keywords(target,
                                                  _from,
                                                  _to,
                                                  class_id)
            return render_template('popular.html',
                                   form=form,
                                   rank=top100)
    return render_template('popular.html',
                           form=form)


def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'repositories')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      show_single_page=show_single_page_or_not(),
                      mode=Pagination.MODE_SIMPLE,
                      **kwargs)


if __name__ == '__main__':
    app.run(debug=True)
