from datetime import datetime

from .database import db


posts_tags_table = db.Table('posts_tags', db.Model.metadata,
                          db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                          db.Column('post_id', db.Integer, db.ForeignKey('posts.id')))


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    posts = db.relationship("Post", secondary=posts_tags_table, back_populates="tags")

    def __repr__(self):
        return "<Tag id={}, name='{}'>".format(self.id, self.name)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    tags = db.relationship("Tag", secondary=posts_tags_table, back_populates="posts")

    def __repr__(self):
        return "<Post id={}, title='{}'>".format(self.id, self.title)
