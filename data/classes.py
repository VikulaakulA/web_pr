import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Class(SqlAlchemyBase):
    __tablename__ = 'classes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    lesson_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("lessons.id"))
    done = sqlalchemy.Column(sqlalchemy.Integer,
                                  default=int)
    user = orm.relationship('User')
    lesson = orm.relationship('Lesson')
