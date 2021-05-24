from flask import Blueprint, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

from ..database import db
from ..models import Post, Tag

posts = Blueprint("posts", __name__)


@posts.route("/")
def index():
    tag_names = request.args.get("tag_names")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    print(date_from, date_to)

    if (tag_names is None or tag_names == "") and (date_from is None or date_from == "") and (date_to is None or date_to == ""):
        posts = Post.query.all()
        return render_template("index.html", posts=posts)

    if tag_names is not None and (date_from is None or date_from == "") and (date_to is None or date_to == ""):
        list_tag_names = tag_names.split()
        posts = Post.query.filter(Post.tags.any(Tag.name.in_(list_tag_names))).all()
        return render_template("index.html", posts=posts, tag_names=tag_names, date_from=date_from, date_to=date_to)

    if (tag_names is None or tag_names == "") and date_from is not None and (date_to is None or date_to == ""):
        posts = Post.query.filter(Post.created_at >= date_from).all()
        return render_template("index.html", posts=posts, tag_names=tag_names, date_from=date_from, date_to=date_to)

    if tag_names is not None and date_from is not None and (date_to is None or date_to == ""):
        list_tag_names = tag_names.split()
        posts = Post.query.filter(db.and_(Post.tags.any(Tag.name.in_(list_tag_names)), Post.created_at <= date_to)).all()
        return render_template("index.html", posts=posts, tag_names=tag_names, date_from=date_from, date_to=date_to)

    if (tag_names is None or tag_names == "") and date_from is not None and date_to is not None:
        posts = Post.query.filter(db.and_(Post.created_at <= date_to, Post.created_at >= date_from)).all()
        return render_template("index.html", posts=posts, tag_names=tag_names, date_from=date_from, date_to=date_to)

    if (tag_names is None or tag_names == "") and (date_from is None or date_from == "") and date_to is not None:
        posts = Post.query.filter(Post.created_at >= date_from).all()
        return render_template("index.html", posts=posts, tag_names=tag_names, date_from=date_from, date_to=date_to)

    if tag_names is not None and (date_from is None or date_from == "") and date_to is not None:
        list_tag_names = tag_names.split()
        posts = Post.query.filter(db.and_(Post.tags.any(Tag.name.in_(list_tag_names)), Post.created_at >= date_from)).all()
        return render_template("index.html", posts=posts, tag_names=tag_names, date_from=date_from, date_to=date_to)

    if tag_names is not None and date_from is not None and date_to is not None:
        list_tag_names = tag_names.split()
        posts = Post.query.filter(db.and_(Post.tags.any(Tag.name.in_(list_tag_names)), db.and_(Post.created_at <= date_to, Post.created_at >= date_from))).all()
        return render_template("index.html", posts=posts, tag_names=tag_names, date_from=date_from, date_to=date_to)


@posts.route("/<int:post_id>")
def post(post_id):
    post = Post.query.get(post_id)
    if not post:
        abort(404)
    return render_template("post.html", post=post)


@posts.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            new_post = Post(title=title, content=content)

            all_tag_names = get_tag_names_from_post(title, content)
            post_tags = []

            for tag_name in all_tag_names:
                tag = get_or_create(db.session, Tag, name=tag_name)
                post_tags.append(tag)

            new_post.tags = post_tags

            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for("posts.index"))
    return render_template("create.html")


@posts.route("/<int:post_id>/edit", methods=("GET", "POST"))
def edit(post_id):
    post = Post.query.get(post_id)

    if not post:
        abort(404)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            post.title = title
            post.content = content

            all_tag_names = get_tag_names_from_post(title, content)
            post_tags = []

            for tag_name in all_tag_names:
                tag = get_or_create(db.session, Tag, name=tag_name)
                post_tags.append(tag)

            post.tags = post_tags

            db.session.commit()

            return redirect(url_for("posts.index"))

    return render_template("edit.html", post=post)


@posts.route("/<int:post_id>/delete", methods=("POST",))
def delete(post_id):
    post = Post.query.get(post_id)
    if not post:
        abort(404)

    db.session.delete(post)
    db.session.commit()

    flash('"{}" was successfully deleted!'.format(post.id))
    return redirect(url_for("posts.index"))


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def get_tag_names_from_post(title, content):
    title_tags = set(set([word[1:] for word in title.split() if word.startswith("#") if len(word[1:]) > 0]))
    content_tags = set(set([word[1:] for word in content.split() if word.startswith("#") if len(word[1:]) > 0]))

    return title_tags.union(content_tags)