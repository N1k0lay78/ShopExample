import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


class Item(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'item'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    short_description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    full_description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("type.id"))
    type = orm.relation('Type')
