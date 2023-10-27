from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, String
from database.database import db

from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    posts = relationship("BlogPost", back_populates="author")  # Use "BlogPost" and "author"
    comments = relationship("Comment", back_populates="comment_author")

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self):
        return {column.name: getattr(self, column.name, None) for column in self.__table__.columns}
