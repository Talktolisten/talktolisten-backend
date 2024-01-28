from app.database import get_db
from app.models import User, Bot, Voice, Message, Chat


db = next(get_db())

# before run the test: export PYTHONPATH=$PWD 
db.query(User).delete()
db.query(Bot).delete()
db.query(Voice).delete()
db.query(Message).delete()
db.query(Chat).delete()

db.commit()
db.close()