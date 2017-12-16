"""Utility file to seed challenge database"""

from sqlalchemy import func
import model
import app

def load_message_types():
    """Add types of allowed message formats."""

    text = model.MessageType(message_type='text')
    image = model.MessageType(message_type='image_link')
    video = model.MessageType(message_type='video_link')

    model.db.session.add(text)
    model.db.session.add(image)
    model.db.session.add(video)
    model.db.session.commit()

if __name__ == "__main__":
    model.connect_to_db(app.app)

    # In case tables haven't been created, create them.
    model.db.create_all()

    load_message_types()
