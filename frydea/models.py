from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from frydea.database import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(256))
    username: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str] = mapped_column(String(256))
    create_time: Mapped[datetime] = mapped_column(comment="用户创建时间")

    cards: Mapped[List['Card']] = relationship(back_populates='user')

    def __init__(self, username=None, nickname=None):
        self.username = username
        self.nickname = nickname if nickname else username
        self.create_time = datetime.now()

    def __repr__(self):
        return f'<User {self.username!r}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password, password)


class Card(db.Model):
    """
    版本号从1开始，第一个版本的update_time就是当前卡片的创建时间
    删除也会生成一个版本号，最后的版本号，比上一个版本号加一，然后取负值
    """
    __tablename__ = 'cards'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    version: Mapped[int] = mapped_column(comment='版本号')
    content: Mapped[str] = mapped_column(comment='Markdown内容')
    create_time: Mapped[datetime] = mapped_column(comment="卡片创建时间")
    update_time: Mapped[datetime] = mapped_column(comment='卡片更新时间')

    user: Mapped['User'] = relationship(back_populates='cards')
    changelogs: Mapped[List['ChangeLog']] = relationship(back_populates='card')

    def __init__(self, user_id=0, version=0, content='', create_time=None, update_time=None):
        self.user_id = user_id
        self.version = version
        self.content = content
        self.create_time = create_time if create_time else datetime.now()
        self.update_time = update_time if update_time else self.create_time 

    def __repr__(self):
        return f'<Card {self.number!r}>'

    def todict(self):
        return {
            'cid': self.id if self.id else 0,
            'version': self.version,
            'content': self.content,
            'createTime': self.create_time.isoformat() if self.create_time else '',
            'updateTime': self.update_time.isoformat() if self.update_time else '',
        }


class ChangeLog(db.Model):
    __tablename__ = 'changelog'
    __table_args__ = (
        UniqueConstraint('card_id', 'version'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    card_id: Mapped[int] = mapped_column(ForeignKey('cards.id'))
    version: Mapped[int] = mapped_column(comment='版本号')
    content: Mapped[str] = mapped_column(comment='Markdown内容')
    create_time: Mapped[datetime] = mapped_column(comment='卡片创建时间')
    update_time: Mapped[datetime] = mapped_column(comment='卡片更新时间')

    card: Mapped['Card'] = relationship(back_populates='changelogs')

    def __init__(self, user_id, card_id, version, content, create_time, update_time):
        self.user_id = user_id
        self.card_id = card_id
        self.version = version
        self.content = content
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return f'<ChangeLog {self.card_id!r}@{self.version}>'
