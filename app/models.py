from sqlalchemy.schema import Column
from sqlalchemy import Integer, String, Boolean, ForeignKey, text, Table, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP, Date
from .database import Base

user_likes_bots = Table('user_likes_bots', Base.metadata,
    Column('user_id', String, ForeignKey('users.user_id'), primary_key=True),
    Column('bot_id', Integer, ForeignKey('bots.bot_id'), primary_key=True),
    Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
)

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, nullable=False, unique=True)
    username= Column(String, nullable=False,unique=True)
    gmail = Column(String, nullable=False,unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    subscription = Column(String, nullable=False,server_default="standard")
    bio = Column(String, nullable=True)
    profile_picture = Column(String, nullable=False)
    status = Column(String, nullable=False,server_default="inactive")
    theme = Column(String, nullable=False,server_default="light")
    liked_bots = relationship('Bot', secondary=user_likes_bots, back_populates='liked_by_users')


class Bot(Base):
    __tablename__ = "bots"

    bot_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    bot_name = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    description = Column(String, nullable=False)
    profile_picture = Column(String, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    voice_id = Column(Integer, ForeignKey(
        "voices.voice_id", ondelete="CASCADE"), nullable=False)
    greeting = Column(String, nullable=False)
    num_chats = Column(Integer, nullable=False,server_default="0")
    likes = Column(Integer, nullable=False,server_default="0")
    created_by = Column(String, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    privacy = Column(String, nullable=False, server_default='public')
    gender = Column(String, nullable=True, server_default='non-binary')
    liked_by_users = relationship('User', secondary=user_likes_bots, back_populates='liked_bots')

class Voice(Base):
    __tablename__ = "voices"

    voice_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    voice_name = Column(String, nullable=False)
    voice_description = Column(String, nullable=False)
    voice_endpoint = Column(String, nullable=False)
    voice_provider = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    language = Column(String, nullable=True, server_default='en-US')
    style = Column(String, nullable=True, server_default='neutral')
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    created_by = Column(String, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    sample_url = Column(String, nullable=False)

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey(
        "chats.chat_id", ondelete="CASCADE"), nullable=True)
    group_chat_id = Column(Integer, ForeignKey(
        "group_chats.group_chat_id", ondelete="CASCADE"), nullable=True)
    message = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    created_by_user = Column(String, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=True)
    created_by_bot =Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), nullable=True)    
    is_bot = Column(Boolean, nullable=False,server_default="false")

    __table_args__ = (
        CheckConstraint('(chat_id IS NOT NULL AND group_chat_id IS NULL) OR (chat_id IS NULL AND group_chat_id IS NOT NULL)', name='chat_id_xor_group_chat_id'),
    )
    
class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    user_id = Column(String, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    bot_id1 = Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), nullable=False)
    bot_id2 = Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), nullable=True)
    bot_id3 = Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), nullable=True)
    bot_id4 = Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), nullable=True)
    bot_id5 = Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    last_message = Column(Integer, ForeignKey("messages.message_id",ondelete="CASCADE"), nullable=True)


class GroupChat(Base):
    __tablename__ = "group_chats"
    group_chat_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    group_chat_name = Column(String, nullable=True)
    user_id = Column(String, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    group_chat_profile_picture = Column(String, nullable=True)
    privacy = Column(String, nullable=False, server_default='public')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    last_message = Column(Integer, ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=True)


class GroupChatBots(Base):
    __tablename__ = "group_chat_bots"
    group_chat_id = Column(Integer, ForeignKey(
        "group_chats.group_chat_id", ondelete="CASCADE"), primary_key=True)
    bot_id = Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    

class FeedbackReport(Base):
    __tablename__ = "feedback_report"
    fr_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    user_id = Column(String, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    feedback = Column(String, nullable=True)
    report = Column(String, nullable=True)
    pictures = Column(ARRAY(String), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class BlockIP(Base):
    __tablename__ = "block_ips"
    ip = Column(String, primary_key=True, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))