# Standard library
import datetime
import json
import uuid

# Third party
import bcrypt
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

# Local modules
import helper
import model


app = flask.Flask(__name__)


@app.errorhandler(400)
def bad_request(error=None):
    resp = flask.jsonify({'status': 400,
                          'msg': 'Bad Request: ' + flask.request.url})
    resp.status_code = 400
    return resp


@app.errorhandler(401)
def unauthorized(error=None):
    resp = flask.jsonify({'status': 401,
                          'msg': 'Unauthorized: ' + flask.request.url})
    resp.status_code = 401
    return resp


@app.errorhandler(415)
def unsupported_media_type(error=None):
    resp = flask.jsonify({'status': 415,
                          'msg': 'Unsupported Media Type: ' + flask.request.url})
    resp.status_code = 415
    return resp


@app.route('/users', methods=['POST'])
def sign_up():
    """Endpoint for adding user to the database.

    Request:
            {
              'username': <username>,
              'password': <password>
            }

    Response:
            {
              'status': <status>,
              'msg': <msg>
            }"""

    user = json.loads(flask.request.data)

    # Only create user if this username isn't already registered and values passed in.
    if not user['username'] or \
       not user['password'] or \
       model.User.query.filter(model.User.username == user['username']).first():
        response = bad_request()
    else:
        # Hash/salt the user's password.
        pw_hash = bcrypt.hashpw(user['password'].encode(), bcrypt.gensalt())
        new_user = model.User(username=user['username'],
                              credentials=pw_hash)
        model.db.session.add(new_user)
        model.db.session.commit()
        response = flask.jsonify({'status': 'OK',
                                  'msg': 'Account successfully registered'})
    return response


@app.route('/log_in', methods=['POST'])
def log_in():
    """Endpoint for logging in.

    Request:
            {
              'username': <username>,
              'password': <password>
            }

    Response:
            {
              'status': <status>,
              'msg': <msg>
            }"""

    credentials = json.loads(flask.request.data)

    user = model.User.query.filter(model.User.username
                                   == credentials['username']).first()

    # If user doesn't exist or password is invalid, throw error.
    if not user or \
       not bcrypt.checkpw(credentials['password'].encode(), user.credentials.encode()):
        return unauthorized()

    # Create a session with a difficult-to-guess ID.
    session_id = uuid.uuid4().hex
    new_session = model.Session(session_id=session_id,
                                user_id=user.user_id)
    model.db.session.add(new_session)
    model.db.session.commit()

    response = flask.jsonify({'status' : 'OK',
                              'msg' : 'Successfully logged in'})
    response.set_cookie('session_id', value=session_id)
    return response


@app.route('/log_out', methods=['GET'])
def log_out():
    """Endpoint for logging out.

    Response:
            {
              'status': <status>,
              'msg': <msg>
            }"""

    user = model.Session.query.filter(model.Session.session_id
                                      == flask.request.cookies.get('session_id')).first()
    # Only log out if user logged in.
    if not user:
        return bad_request()

    model.db.session.delete(user)
    model.db.session.commit()
    response = flask.jsonify ({'status' : 'OK',
                               'msg' : 'User successfully logged out'})
    return response


@app.route('/messages', methods=['POST'])
def send_message():
    """Endpoint to accept a sender, recipient and message and insert them into the data store.

    The server will make its best effort attempt to set message type
    based on the mime type of the message content.

    Request:
            {
              'sender_id': <sender_id>,
              'recipient_id': <recipient_id>,
              'message_content': <message_content>
            }

    Response:
            {
              'status': <status>,
              'msg':
                    {
                      'type': <type>,
                      'content': <content>,
                      'timestamp': <timestamp>
                    }
            }"""

    message = json.loads(flask.request.data)
    session = model.Session.query.filter(model.Session.session_id
                                         == flask.request.cookies.get('session_id')).first()

    # Only accept message if a token was passed with the request,
    # the token returns the correct user ID,
    # and the recipient is valid.
    if not session or \
       session.user_id != int(message['sender_id']) or \
       not helper.verify_user(message['recipient_id']):

        return bad_request()

    conversation_id = helper.make_conversation_id(message['sender_id'],
                                                  message['recipient_id'])
    timestamp = datetime.datetime.utcnow()

    if message['message_content'].startswith('http'):

        # For purposes of the challenge, meta data is harcoded.
        # In practice, image width, height are included in magic.from_buffer return value.
        if helper.is_image(message['message_content']):
            message_type = model.MessageType.query.filter(model.MessageType.message_type
                                                          == 'image_link').first()
            message_metadata = {'img_width': '300',  # Image width is stored in px.
                                'img_height': '500'}  # Image height is stored in px.

        # For purposes of the challenge, meta data is harcoded.
        # In practice, consider extracting domain name from HTTP header
        # & vid_length from APIs for whitelisted video platforms.
        elif helper.is_video(message['message_content']):
            message_type = model.MessageType.query.filter(model.MessageType.message_type
                                                          == 'video_link').first()
            message_metadata = {'vid_length': '180',  # Video length is stored in seconds.
                                'vid_source': 'youtube'}
        else:
            return unsupported_media_type()

    else:
        message_type = model.MessageType.query.filter(model.MessageType.message_type
                                                      == 'text').first()
        message_metadata = {}

    message_id = message_type.message_type_id
    new_message = model.Message(conversation_id=conversation_id,
                                sender_id=message['sender_id'],
                                recipient_id=message['recipient_id'],
                                message_type=message_id,
                                message_content=message['message_content'],
                                timestamp=timestamp,
                                message_metadata=json.dumps(message_metadata))
    model.db.session.add(new_message)
    model.db.session.commit()
    response = flask.jsonify({'status': 'OK',
                              'msg':{'type': message_type.message_type,
                                     'content': message['message_content'],
                                     'timestamp': timestamp}})
    return response


@app.route('/messages', methods=['GET'])
def fetch_messages():
    """Endpoint to accept two users and load all messages sent between them.

    Request:
            {
              'user_id_1': <user_id_1>,
              'user_id_2': <user_id_2>,
              'page': <page>,
              'messages_per_page': <messages_per_page>
            }

    Response:
            {
              'status': <status>,
              'msg': <msg>
            }"""

    # Only return messages if user logged in and IDs are valid.
    if not model.Session.query.filter(model.Session.session_id
                                      == flask.request.cookies.get('session_id')).first() or \
       not helper.verify_user(flask.request.args.get('user_id_1')) or \
       not helper.verify_user(flask.request.args.get('user_id_2')):

        return bad_request()

    conversation_id = helper.make_conversation_id(flask.request.args.get('user_id_1'),
                                                  flask.request.args.get('user_id_2'))
    # Support for pagination with default values.
    if flask.request.args.get('page') and \
       flask.request.args.get('messages_per_page'):
        page = int(flask.request.args.get('page'))
        messages_per_page = int(flask.request.args.get('messages_per_page'))
    else:
        page = 1
        messages_per_page = 20

    # Sort by descending time.
    fetched_messages = (model.Message.query.filter(model.Message.conversation_id
                                                   == conversation_id)
                                           .order_by(model.Message.timestamp.desc())
                                           .paginate(page, messages_per_page))
    response = flask.jsonify({'status': 'OK',
                              'msg': helper.pgs_to_dict(fetched_messages)})
    return response


if __name__ == "__main__":
    app.debug = False
    app.jinja_env.auto_reload = app.debug  # Makes sure templates, etc. are not cached if debug mode on.

    model.connect_to_db(app)

    # Use the DebugToolbar.
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
