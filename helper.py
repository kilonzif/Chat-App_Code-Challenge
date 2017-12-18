"""HELPER FUNCTIONS FOR APP"""

import jsonpickle
import magic
import urllib2

# Local modules
import model

# Most common video / image file formats
VIDEO_FORMATS = ['AVI', 'FLV', 'WMV', 'MOV', 'MP4']
IMAGE_FORMATS = ['JPEG', 'JPG', 'JFIF', 'Exif', 'TIFF', 'GIF', 'BMP', 'PNG', 'PPM', 'PGM', 'PBM', 'PNM']


def verify_user(user_id):
    """Takes a user ID and returns True if the ID is verified."""

    if not model.User.query.filter(model.User.user_id == user_id).first():
        return False

    return True


def make_conversation_id(user1, user2):
    """Takes in two users, deterministically sorts them, and returns a string
    to be used as a conversation ID."""

    users = []
    users.append(user1)
    users.append(user2)
    users.sort()
    conversation_id = '-'.join(users)

    return conversation_id


def is_image(link):
    """Takes in a link as message content, returns True if the file type is an image."""

    try:
        link_content = urllib2.urlopen(link)
        message_content = magic.from_buffer(link_content.read())
        for format in IMAGE_FORMATS:
            if format in message_content:
                return True

        return False

    except:
        return False


def is_video(link):
    """Takes in a link as message content, returns True if the file type is a video."""

    try:
        link_content = urllib2.urlopen(link)
        message_content = magic.from_buffer(link_content.read())
        for format in VIDEO_FORMATS:
            if format in message_content:
                return True

        return False

    except:
        return False


def pgs_to_dict(fetched_messages):
    """Takes a Pagination object and returns a dictionary."""

    result = {}
    result['page'] = fetched_messages.page
    result['per_page'] = fetched_messages.per_page
    result['has_next'] = fetched_messages.has_next
    result['has_prev'] = fetched_messages.has_prev
    result['pages'] = fetched_messages.pages

    fetched_messages = fetched_messages.items

    for message in fetched_messages:
        result[message.message_id] = jsonpickle.encode(message)

    return result
