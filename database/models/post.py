from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, String, Text
from database.database import db


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    author = relationship("User", back_populates="posts")  # Use "User" and "posts"

    comments = relationship("Comment", back_populates="parent_post")


def __repr__(self):
    return f'<BlogPost {self.title}>'


def to_dict(self):
    return {column.name: getattr(self, column.name, None) for column in self.__table__.columns}
