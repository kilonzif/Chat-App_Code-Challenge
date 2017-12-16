"""HELPER FUNCTIONS FOR APP"""

import urllib2
import magic

# Most common video / image file formats
VIDEO_FORMATS = ['AVI', 'FLV', 'WMV', 'MOV', 'MP4']
IMAGE_FORMATS = ['JPEG', 'JPG', 'JFIF', 'Exif', 'TIFF', 'GIF', 'BMP', 'PNG', 'PPM', 'PGM', 'PBM', 'PNM']


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
