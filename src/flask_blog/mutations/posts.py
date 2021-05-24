import graphene
from graphene import relay

from .. import models, types
from ..database import db


class CreatePostInput:
    title = graphene.String(required=True)
    content = graphene.String(required=True)


class EditPostInput:
    id = graphene.Int(required=True)
    title = graphene.String(required=True)
    content = graphene.String(required=True)

class DeletePostInput:
    id = graphene.Int(required=True)

class FilterPostInput:
    tag_names = graphene.String(required=False)
    date_from = graphene.String(required=False)
    date_to = graphene.String(required=False)


class CreatePostSuccess(graphene.ObjectType):
    post = graphene.Field(types.PostNode, required=True)


class EditPostSuccess(graphene.ObjectType):
    post = graphene.Field(types.PostNode, required=True)

class FilterPostSuccess(graphene.ObjectType):
    post = graphene.List(types.PostNode, required=True)


class DeletePostSuccess(graphene.ObjectType):
    post = graphene.Field(types.PostNode, required=True)


class CreatePostOutput(graphene.Union):
    class Meta:
        types = (CreatePostSuccess,)


class EditPostOutput(graphene.Union):
    class Meta:
        types = (EditPostSuccess,)


class DeletePostOutput(graphene.Union):
    class Meta:
        types = (DeletePostSuccess,)

class FilterPostOutput(graphene.Union):
    class Meta:
        types = (FilterPostSuccess,)


class CreatePost(relay.ClientIDMutation):
    Input = CreatePostInput
    Output = CreatePostOutput

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        new_post = models.Post(**input)

        db.session.add(new_post)
        db.session.commit()

        return CreatePostSuccess(post=new_post)


class EditPost(relay.ClientIDMutation):
    Input = EditPostInput
    Output = EditPostOutput

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        edited_post = edit_post(**input)
        return EditPostSuccess(post=edited_post)

class DeletePost(relay.ClientIDMutation):
    Input = DeletePostInput
    Output = DeletePostOutput

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        deleted_post = delete_post(**input)
        return DeletePostSuccess(post=deleted_post)

class FilterPost(relay.ClientIDMutation):
    Input = FilterPostInput
    Output = FilterPostOutput

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        filtered_posts = filter_posts(**input)
        return FilterPostSuccess(post=filtered_posts)

        


def edit_post(id, title, content):
    print(id, title, content)
    edited_post = models.Post.query.get(id)
    edited_post.title = title
    edited_post.content = content
    db.session.commit()
    return edited_post


def delete_post(id):
    print(id)
    deleted_post = models.Post.query.get(id)
    if not deleted_post:
        abort(404)

    db.session.delete(deleted_post)
    db.session.commit()
    return deleted_post

def filter_posts(tag_names, date_from, date_to):
    if (tag_names is None or tag_names == "") and (date_from is None or date_from == "") and (date_to is None or date_to == ""):
        posts = models.Post.query.all()
        return posts

    if tag_names is not None and (date_from is None or date_from == "") and (date_to is None or date_to == ""):
        list_tag_names = tag_names.split()
        posts = models.Post.query.filter(models.Post.tags.any(models.Tag.name.in_(list_tag_names))).all()
        return posts

    if (tag_names is None or tag_names == "") and date_from is not None and (date_to is None or date_to == ""):
        posts = models.Post.query.filter(models.Post.created_at >= date_from).all()
        return posts

    if tag_names is not None and date_from is not None and (date_to is None or date_to == ""):
        list_tag_names = tag_names.split()
        posts = models.Post.query.filter(db.and_(models.Post.tags.any(models.Tag.name.in_(list_tag_names)), models.Post.created_at <= date_to)).all()
        return posts

    if (tag_names is None or tag_names == "") and date_from is not None and date_to is not None:
        posts = models.Post.query.filter(db.and_(models.Post.created_at <= date_to, models.Post.created_at >= date_from)).all()
        return posts

    if (tag_names is None or tag_names == "") and (date_from is None or date_from == "") and date_to is not None:
        posts = models.Post.query.filter(models.Post.created_at >= date_from).all()
        return posts

    if tag_names is not None and (date_from is None or date_from == "") and date_to is not None:
        list_tag_names = tag_names.split()
        posts = models.Post.query.filter(db.and_(models.Post.tags.any(models.Tag.name.in_(list_tag_names)), models.Post.created_at >= date_from)).all()
        return posts

    if tag_names is not None and date_from is not None and date_to is not None:
        list_tag_names = tag_names.split()
        posts = models.Post.query.filter(db.and_(models.Post.tags.any(models.Tag.name.in_(list_tag_names)), db.and_(models.Post.created_at <= date_to, Post.created_at >= date_from))).all()
        return posts
