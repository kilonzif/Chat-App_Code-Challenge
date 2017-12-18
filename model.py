from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    credentials = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        """Readable info about the user."""

        return "<User username={}>".format(self.username)


class MessageType(db.Model):
    """Message type model."""

    __tablename__ = 'message_types'

    message_type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    message_type = db.Column(db.String(36), nullable=False)

    def __repr__(self):
        """Readable info about the message type."""

        return "<Message type={}>".format(self.message_type)


class Message(db.Model):
    """Message model."""

    __tablename__ = 'messages'

    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    conversation_id = db.Column(db.String(255), index=True, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message_type = db.Column(db.Integer, db.ForeignKey('message_types.message_type_id'), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    message_metadata = db.Column(db.JSON, nullable=False)

    sender = db.relationship("User", foreign_keys="[Message.sender_id]")
    recipient = db.relationship("User", foreign_keys="[Message.recipient_id]")

    def __repr__(self):
        """Readable info about the message."""

        return "<Message: sender={} date={} content={}>".format(self.sender_id, self.timestamp, self.message_content)


class Session(db.Model):
    """Session model."""

    __tablename__ = 'sessions'

    session_id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repr__(self):
        """Readable info about the session."""

        return "<Session user={} id={}>".format(self.user_id, self.session_id)


##############################################################################
# Helper functions

def init_app():
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


def connect_to_db(app, db_uri='postgres:///challenge'):
    """Connect the database to our Flask app."""

    # Configure to use challenge database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///challenge'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")