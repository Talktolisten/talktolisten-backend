from sqlalchemy.schema import Column
from sqlalchemy import Integer, String, Boolean, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, nullable=False, unique=True)
    username= Column(String, nullable=False,unique=True)
    gmail = Column(String, nullable=False,unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    subscription = Column(String, nullable=False,server_default="standard")
    bio = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    status = Column(String, nullable=False,server_default="inactive")
    theme = Column(String, nullable=False,server_default="light")


class Bot(Base):
    __tablename__ = "bots"

    bot_id = Column(Integer, primary_key=True, nullable=False)
    bot_name = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    description = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    voice_id = Column(Integer, ForeignKey(
        "voices.voice_id", ondelete="CASCADE"), nullable=False)
    num_chats = Column(Integer, nullable=False,server_default="0")
    likes = Column(Integer, nullable=False,server_default="0")
    created_by = Column(String, ForeignKey(
        "users.username", ondelete="CASCADE"), nullable=False)

class Voice(Base):
    __tablename__ = "voices"

    voice_id = Column(Integer, primary_key=True, nullable=False)
    voice_name = Column(String, nullable=False)
    voice_description = Column(String, nullable=True)
    voice_endpoint = Column(String, nullable=False)
    voice_provider = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    created_by = Column(String, ForeignKey(
        "users.username", ondelete="CASCADE"), nullable=False)

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, nullable=False)
    chat_id = Column(Integer, ForeignKey(
        "chats.chat_id", ondelete="CASCADE"), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    created_by_user = Column(String, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=True)
    created_by_bot =Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), nullable=True)    
    is_bot = Column(Boolean, nullable=False,server_default="false")
    
class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(Integer, primary_key=True, nullable=False, unique=True)
    user_id = Column(String, ForeignKey(
        "users.username", ondelete="CASCADE"), primary_key=True)
    bot_id1 = Column(Integer, ForeignKey(
        "bots.bot_id", ondelete="CASCADE"), primary_key=True, nullable=False)
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


