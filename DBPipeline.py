from SettingLoder import FollowUp,TimePeriod
from datetime import datetime
import json
import sqlite3
from SettingLoder import FOLLOWUPSETTING
class DBInstance(object):
    def __init__(self):
        self.con = sqlite3.connect("DB/Database.sqlite")
        self.cur = self.con.cursor()
        self.createTablesIfNotExist()

    def getConnection(self):
        return self.con

    def getCursor(self):
        return self.cur

    def createTablesIfNotExist(self):
        self.createChatHistoryStore()

    def createChatHistoryStore(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS CHATHISTORY (
                id INTEGER PRIMARY KEY,
                userid TEXT NOT NULL,
                username TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                createdon DATETIME DEFAULT CURRENT_TIMESTAMP,
                tag TEXT DEFAULT 'chat',
                followupTrack TEXT
            ); """)

    def insertChatHistory(self, userid, username, role, content, tag='chat'):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        self.cur.execute("""
            INSERT INTO CHATHISTORY (userid, username, role, content, createdon, tag)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (userid, username, role, content, formatted_datetime, tag))
        self.con.commit()
    
    def getFollowUPTrackByUserId(self,userid):
        self.cur.execute("""
            SELECT id, followupTrack FROM CHATHISTORY
            WHERE userid = ?
            ORDER BY createdon
        """, (userid,))
        records = self.cur.fetchall()
        final=[{"id": id, "data": data} for id,data in records][-1]
        if not final['data']:
            return FOLLOWUPSETTING,final['id']

        follow_up = FollowUp()
        for key, value in json.loads(final['data']).items():
            setattr(follow_up, key, TimePeriod(**value))
        return follow_up,final['id']
    
    def updateFollowUpTrackByUserId(self,row_id,followupTrack):
        self.cur.execute("UPDATE CHATHISTORY SET followupTrack=? WHERE id=?", (followupTrack, row_id))
        self.con.commit()


    def getUserIds(self):
        self.cur.execute("""
            SELECT DISTINCT userid FROM CHATHISTORY
        """)
        unique_userids = [row[0] for row in self.cur.fetchall()]
        return unique_userids

    def deleteChatHistoryById(self, row_id):
        self.cur.execute("DELETE FROM CHATHISTORY WHERE id=?", (row_id,))
        self.con.commit()

    def updateChatHistoryContentById(self, row_id, new_content):
        self.cur.execute("UPDATE CHATHISTORY SET content=? WHERE id=?", (new_content, row_id))
        self.con.commit()

    def truncateTable(self):
        # Truncate (delete all data) from a specific table
        try:
            self.cur.execute(f"DELETE FROM CHATHISTORY")
            self.con.commit()
            print(f"CHATHISTORY table truncated successfully.")
        except sqlite3.Error as e:
            print(f"Error truncating CHATHISTORY table: {e}")

    def deleteChatHistoryByUserID(self, userid):
        # Delete all data for a specific userid
        try:
            self.cur.execute("DELETE FROM CHATHISTORY WHERE userid=?", (userid,))
            self.con.commit()
            print(f"Chat history for userid '{userid}' deleted successfully.")
        except sqlite3.Error as e:
            print(f"Error deleting chat history for userid '{userid}': {e}")


    def getChatHistoryByUserID(self, userid):
        self.cur.execute("""
            SELECT id, role, content, createdon, tag FROM CHATHISTORY
            WHERE userid = ?
            ORDER BY createdon
        """, (userid,))
        records = self.cur.fetchall()
        return [{"id": id, "role": role, "content": content, "createdon": createdon, "tag": tag}
                for id, role, content, createdon, tag in records]

    def get_username_by_userid(self, userid):
        self.cur.execute("SELECT username FROM CHATHISTORY WHERE userid = ? LIMIT 1", (userid,))
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return None

