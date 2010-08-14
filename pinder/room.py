"Room object"
import datetime

from pinder.connector import HTTPConnector

class Room(object):
    def __init__(self, campfire, room_id, data, connector=HTTPConnector):
        self._campfire = campfire
        connector = connector or HTTPConnector
        self._connector = connector
        # The id of the room
        self.id = room_id
        # The raw data of the room
        self.data = data
        # The name of the room
        self.name = data["name"]

    def __repr__(self):
        return "<Room: %s>" % self.id

    def __eq__(self, other):
        return self.id == other.id
        
    def _path_for_room(self, path):
        uri = 'room/%s' % self.id
        if path:
            uri = '%s/%s' % (uri, path)
        return uri
 
    def _get(self, path='', data=None, headers=None):
        return self._connector.get(self._path_for_room(path), data, headers)

    def _post(self, path, data=None, headers=None, file_upload=False):
        return self._connector.post(
            self._path_for_room(path), data, headers, file_upload)
        
    def _put(self, path, data=None, headers=None):
        return self._connector.put(self._path_for_room(path), data, headers)

    def _send(self, message, type_='TextMessage'):
        data = {'message': {'body': message, 'type': type_}}
        return self._post('speak', data)

    def join(self):
        "Joins the room."
        self._post("join")

    def leave(self):
        "Leaves the room."
        self._post("leave")
        
    def lock(self):
        "Locks the room to prevent new users from entering."
        self._post("lock")

    def unlock(self):
        "Unlocks the room."
        self._post("unlock")

    def users(self):
        "Gets info about users chatting in the room."
        return self._campfire.users(self.data['name'])
        
    def transcript(self, date=None):
        ("Gets the transcript for the given date "
        "(a datetime.date instance) or today.")
        date = date or datetime.date.today()
        transcript_path = "transcript/%s/%s/%s" % (
            date.year, date.month, date.day)
        return self._get(transcript_path)['messages']

    def speak(self, message):
        "Sends a message to the room. Returns the message data."
        return self._send(message, type_='TextMessage')['message']

    def paste(self, message):
        "Pastes a message to the room. Returns the message data."
        return self._send(message, type_='PasteMessage')['message']

    def sound(self, message):
        "Plays a sound into the room. Returns the message data."
        return self._send(message, type_='SoundMessage')['message']
    
    def update(self, name, topic):
        "Updates name and/or topic of the room."
        data = {'room': {'name': name, 'topic': topic}}
        self._put('', data)

    def uploads(self):
        "Lists recently uploaded files."
        return self._get('uploads')['uploads']

    def upload(self, fileobj):
        "Uploads the content of the given file-like object to the room."
        data = {'upload': fileobj}
        return self._post('uploads', data, file_upload=True)['upload']

    def recent_messages(self, limit=100, since_message_id=None):
        ("Returns upto limit (max 100) messages optionally "
        "starting from since_message_id.")
        data = dict(limit=limit, since_message_id=since_message_id)
        return self._get('recent', data)['messages']
