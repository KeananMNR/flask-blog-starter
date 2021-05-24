from flask_blog import create_app
from flask_blog.database import db
from flask_blog.models import Post, Tag


def run():
    app = create_app()
    with app.app_context():
        first_tag = Tag(
            name="fire"
        )

        first_post = Post(
            title="First Post", content="Content for the first post"
        )
        second_post = Post(
            title="Second Post", content="Content for the second post"
        )
        
        second_post.tags.append(first_tag)

        db.session.add(first_tag)
        db.session.add(first_post)
        db.session.add(second_post)
        db.session.commit()


if __name__ == "__main__":
    run()
