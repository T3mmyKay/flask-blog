from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, Text
from database.database import db


class Comment(db.Model):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('blog_posts.id'), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    parent_post = relationship("BlogPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")

    def __repr__(self):
        return f'<Comment {self.id}>'

    def to_dict(self):
        return {column.name: getattr(self, column.name, None) for column in self.__table__.columns}
