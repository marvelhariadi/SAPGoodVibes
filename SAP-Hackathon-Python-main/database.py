import sqlite3 as sl


# TODO: include debug print statements

class Database:
    """A class storing information in a sqlite3 database

    tables:
        users:
            id: INTEGER: a unique identifier for a particular user
            name: TEXT: the name of a user
            SlackID: TEXT: TODO depends on Wenjie's results

        rooms:
            id: INTEGER: a unique identifier for the room
            name: TEXT: the displayed name for the room
            description: TEXT: a description of the room, including its amenities
            open: TEXT: the time the room becomes available in ISO time format 'YYYY-MM-DD HH:MM'
            close: TEXT: the time the room closes in ISO time format 'YYYY-MM-DD HH:MM'

        events:
            id: INTEGER: a unique identifier for the event
            name: TEXT: the displayed name for the event
            description: the displayed description of the event
            room_id: INTEGER: the room where the event takes place
            organizer_id: INTEGER: the id of the user who created this event
            start_time: TEXT: the start time of the event
            end_time: TEXT: the end time of the event

            an start can be the same as the end of another event with the same roomID
            you cannot have an event with a start or end between the start or end

        events_users: ties users to events they have signed up to attend
            eventID: INTEGER: the identifier for an event in events
            userID: INTEGER: the identifier for a user in users
    """

    def __init__(self, dbname: str):
        if not dbname.endswith('.db'):
            self.con = sl.connect(dbname + '.db')
        else:
            self.con = sl.connect(dbname)
        with self.con:
            self.con.execute("PRAGMA foreign_keys = ON")
            self.con.execute(
                """CREATE TABLE IF NOT EXISTS
                  users(id INTEGER PRIMARY KEY,
                        name TEXT,
                        slack_id TEXT
                        );
                """)
            self.con.execute(
                """CREATE TABLE IF NOT EXISTS rooms(
                  id INTEGER PRIMARY KEY,
                  name TEXT,
                  description TEXT,
                  img TEXT
                  );
                """)
            self.con.execute(
                """CREATE TABLE IF NOT EXISTS events(
                  id INTEGER PRIMARY KEY,
                  name TEXT,
                  description TEXT,
                  room_id INTEGER REFERENCES rooms(id),
                  organizer_id INTEGER,
                  start_time TEXT,
                  end_time TEXT
                  );
                """)
            self.con.execute(
                """CREATE TABLE IF NOT EXISTS events_users(
                 event_id INTEGER REFERENCES events(id),
                 user_id INTEGER REFERENCES users(id),
                 UNIQUE (event_id, user_id)
                 );
                """)
        #     TODO: this probably needs actions to happen if we delete an event from the events table
        self.con.commit()

    def add_user(self, name, slack_id=None):
        """Add the specified user to the users table and returns the ID of the user"""
        cur = self.con.cursor()
        cur.execute(f'INSERT INTO users (id, name, slack_id) VALUES (NULL, ?,?)', (name, slack_id))
        self.con.commit()
        return cur.lastrowid

    def add_event(self, name: str, description: str, room_id: int, organizer_id: int, start_time: str, end_time: str):
        """Add an event to the database

        :param name: name of the event
        :param description: description of the event
        :param room_id: id of the room the event takes place in
        :param organizer_id: id of the user who created the event
        :param start_time: time the event starts in ISO format, YYYY-MM-DD HH:MM
        :param end_time: time the event ends in ISO format, YYYY-MM-DD HH:MM
        :raises KeyError: if there are no entries corresponding to room_id or organizer_id
        :return: event_id: ID of the newly created event
        """
        if self.con.execute("""SELECT EXISTS(
            SELECT 1 FROM events WHERE room_id=?
                                   AND ((start_time = ? OR (start_time < ? AND ? < end_time))
                                          OR (end_time = ? OR (start_time < ? AND ? < end_time))) LIMIT 1)""",
                            (room_id,
                             start_time, start_time, start_time,
                             end_time, end_time, end_time)).fetchone()[0]:
            raise ValueError(f'room with id {room_id} is booked for some or all of that time')
        cur = self.con.cursor()
        cur.execute("""INSERT INTO events(
                         id, name, description, room_id, organizer_id, start_time, end_time) VALUES (?,?,?,?,?,?,?)""",
                    (None, name, description, room_id, organizer_id, start_time, end_time))
        self.con.execute("""INSERT INTO events_users(event_id, user_id) VALUES (?,?)""",
                         (cur.lastrowid, organizer_id))
        event_id = cur.lastrowid
        cur.close()
        self.con.commit()
        return event_id

    def sign_up(self, user_id, event_id):
        self.con.execute("INSERT INTO events_users (user_id, event_id) VALUES (?,?)", (user_id, event_id))
        self.con.commit()

    def lookup_event(self, event_id):
        """Returns a dict containing:
        event id, location, start-time, end-time, creator, attendees
        """
        pass
    #
    # def get_attendees(self, event_id):
    #     attendee_ids = self.con.execute("SELECT user_id FROM event_users WHERE event_id=?", (event_id,))
