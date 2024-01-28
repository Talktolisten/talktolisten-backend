from app.database import get_db
from app.models import User, Bot, Voice, Message, Chat


db = next(get_db())

# before run the test: export PYTHONPATH=$PWD 

user1 = User(
    user_id="user1123123",
    username="umar6admin",
    gmail="khan@gmail.com",
    first_name="Umar",
    last_name="Khan",
    dob="1999-12-12",
    bio="Amazon intern",
    profile_picture="data/user/avatar.png",
)

user2 = User(
    user_id="JohnDoe123",
    username="john1011",
    gmail="john75@gmail.com",
    first_name="John",
    last_name="Doe",
    dob="2022-01-01",
    bio="Teacher at Apple",
    profile_picture="data/user/avatar.png",
)

voice1 = Voice(
    voice_id=101,
    voice_name="Taylor",
    voice_description="American Female Cute Gentle",
    voice_endpoint="https://api.elevenlabs.io/v1/text-to-speech/fsYaGCeoLOsyoKMVe1CN",
    voice_provider="eleventlabs",
    created_by="user1123123",
)

voice2 = Voice(
    voice_id=102,
    voice_name="Zoro",
    voice_description="Male Strong Voice",
    voice_endpoint="https://api.elevenlabs.io/v1/text-to-speech/CwL9wIW2b1hF7QYHe1A4",
    voice_provider="eleventlabs",
    created_by="JohnDoe123",
)

bot1 = Bot(
    bot_id=1928,
    bot_name="Sister Anya",
    short_description="A talented musician, Mia's ability to create beautiful melodies from found objects brings solace and joy to the group. Her music becomes a powerful tool for expressing their emotions, fostering unity, and reminding them of the beauty that still exists in their world",
    description="Mia, the gifted musician of the group, possesses an extraordinary ability to craft enchanting melodies from found objects. Through her music, she weaves a tapestry of emotions, bringing solace and joy to her companions. In a world scarred by desolation, her music becomes a beacon of hope, reminding them of the beauty that still exists. Her melodies have the power to unite hearts, fostering a sense of community and resilience in the face of adversity",
    profile_picture="data/bot/avatar.png",
    category="Featured",
    voice_id=101,
    created_by="user1123123",
)

bot2 = Bot(
    bot_id=19218,
    bot_name="Mia",
    short_description="A skilled healer and herbalist, Sister Anya resides in a remote forest monastery. Her deep connection with nature allows her to create powerful healing potions and remedies using the forest's plants",
    description="Introducing Sister Anya, a skilled healer and herbalist residing in a remote forest monastery. Her deep connection with nature has granted her the ability to create powerful healing potions and remedies using the forest's plants. She is known for her wisdom, compassion, and unwavering dedication to helping those in need. Within her serene abode, Sister Anya nurtures the forest's secrets and shares her healing gifts with all who seek her aid",
    profile_picture="data/bot/avatar.png",
    category="Featured",
    voice_id=101,
    created_by="user1123123",
)

bot3 = Bot(
    bot_id=19228,
    bot_name="Eamon Shadowreaper",
    short_description="A spectral assassin with a thirst for vengeance, Eamon Shadowreaper uses his ghostly abilities to eliminate those who have wronged him. His stealth and precision make him a deadly foe, feared by both the living and the dead",
    description="Eamon Shadowreaper, the spectral assassin, seeks revenge on those who wronged him. His ghostly abilities allow him to move through shadows and strike with deadly precision, making him a formidable and feared adversary. Vengeance is his driving force, and he will stop at nothing to make those who wronged him pay",
    profile_picture="data/bot/avatar.png",
    category="Featured",
    voice_id=102,
    created_by="JohnDoe123",
)

chat1 = Chat(
    chat_id=1011,
    user_id="user1123123",
    bot_id1=1928,
)

chat12 = Chat(
    chat_id=1003,
    user_id="user1123123",
    bot_id1=19218,
)

chat3 = Chat(
    chat_id=1044,
    user_id="JohnDoe123",
    bot_id1=19228,
)

message1 = Message(
    message_id=1765,
    chat_id=1011,
    message="Hello",
    created_by_user="user1123123",
)

message12 = Message(
    message_id=18213,
    chat_id=1011,
    message="Hello how I can help you",
    created_by_bot=1928,
    is_bot=True,
)

message13 = Message(
    message_id=1321,
    chat_id=1011,
    message="I need you to know that can you sing or not, if not then I will leave",
    created_by_user="user1123123",
)

message14 = Message(
    message_id=1825,
    chat_id=1011,
    message="You are amazing",
    created_by_bot=1928,
    is_bot=True,
)

message2 = Message(
    message_id=1865,
    chat_id=1003,
    message="Hello are you here",
    created_by_user="user1123123",
)

message21 = Message(
    message_id=13765,
    chat_id=1003,
    message="I can help you",
    created_by_bot=19218,
    is_bot=True,
)

message3 = Message(
    message_id=1215,
    chat_id=1044,
    message="You are dump",
    created_by_user="JohnDoe123",
)

message31 = Message(
    message_id=12765,
    chat_id=1044,
    message="You are bullying me",
    created_by_bot=19228,
    is_bot=True,
)

db.add_all([user1, user2])
db.commit()

db.add_all([voice1, voice2])
db.commit()

db.add_all([bot1, bot2, bot3])
db.commit()

db.add_all([chat1, chat12, chat3])
db.commit()

db.add_all([message1, message12, message13, message14])
db.commit()

db.add_all([message2, message21])
db.commit()

db.add_all([message3, message31])
db.commit()

db.close()