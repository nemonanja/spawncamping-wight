from datetime import datetime
import time, sqlite3, sys, re, os
 
DEFAULT_DB_PATH = 'db/project.db'
DEFAULT_SCHEMA = 'db/project_schema_dump.sql'
DEFAULT_DATA_DUMP = 'db/project_data_dump.sql'
 
class ProjectDatabase(object):
    '''API to access project DB'''
 
    def __init__(self, db_path=None):
        super(ProjectDatabase, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH


    #Setting up the database. Used for the tests.
    #SETUP, POPULATE and DELETE the database
    def clean(self):
        '''
        Purge the database removing old values.
        '''
        os.remove(self.db_path)

    def load_init_values(self):
        '''
        Populate the database with initial values. It creates
        '''
        self.create_tables_from_schema()
        self.load_table_values_from_dump()

    def create_tables_from_schema(self, schema=None):
        '''
        Create programmatically the tables from a schema file.
        schema contains the path to the .sql schema file. If it is None,
        DEFAULT_SCHEMA is used instead.
        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        with open (schema) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    def load_table_values_from_dump(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.
        dump is the  path to the .sql dump file. If it is None,
        DEFAULT_DATA_DUMP is used instead.
        '''
        con = sqlite3.connect(self.db_path)
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open (dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    def update_username(self, old_username, new_username):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'UPDATE users SET nickname=? WHERE nickname=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (new_username, old_username)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return False
            return True

 
    def get_users(self):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "SELECT nickname FROM USERS"
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(stmnt)
            rows = cur.fetchall()
            if cur.rowcount is None:
                return False
            users = []
            for row in rows:
                nickname = dict(nickname=row[0])
                users.append(nickname)
            return users

    def get_user(self, user_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "SELECT nickname FROM USERS \
                    WHERE id = ?"
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (user_id,)
            cur.execute(stmnt, pvalue)
            row = cur.fetchone()
            if row is None:
                return None
            nickname = row[0]
            return nickname

    def get_role(self, user_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "SELECT role FROM USERS \
                    WHERE id = ?"
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (user_id,)
            cur.execute(stmnt, pvalue)
            row = cur.fetchone()
            if row is None:
                return None
            role = row[0]
            return role

    def add_user(self, nickname, email, role, boss):
        keys_on = 'PRAGMA foreign_keys = ON'
        if role not in ['member', 'leader']:
            return False
        stmnt = "INSERT INTO USERS (nickname, email, role, boss) VALUES (?,?,?,?)"
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (nickname, email, role, boss)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return False
            return True

    def delete_user(self, user_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "DELETE FROM USERS WHERE id=?"
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (user_id,)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 0:
                return False
            return True

    def get_team(self, leader_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "SELECT nickname FROM USERS WHERE boss=? OR id=?"
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (leader_id, leader_id)
            cur.execute(stmnt, pvalue)
            rows = cur.fetchall()
            if cur.rowcount is None:
                return False
            team = []
            for row in rows:
                nickname = dict(nickname=row[0])
                team.append(nickname)
            return team

    def add_to_team(self, user_id, leader_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "UPDATE USERS SET boss=? WHERE id=?"
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (leader_id, user_id)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 0:
                return False
            return True

    def remove_from_team(self, user_id, leader_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "UPDATE USERS SET boss=NULL WHERE id=? AND boss=?"
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (user_id, leader_id)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 0:
                return False
            return True

    def update_title(self, task_id, title):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'UPDATE tasks SET title=? WHERE id=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (title, task_id)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return False
            return True

    def update_description(self, task_id, description):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'UPDATE tasks SET description=? WHERE id=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (description, task_id)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return False
            return True

    def update_category(self, task_id, category):
        allowed = ["frontend", "backend", "UX", "bug"]
        if category not in allowed:
            return False
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'UPDATE tasks SET category=? WHERE id=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (category, task_id)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return False
            return True


    def get_user_id(self, username):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "SELECT id FROM users \
                    WHERE nickname = ?"
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (username,)
            cur.execute(stmnt, pvalue)
            row = cur.fetchone()
            if row is None:
                return False
            userid = row[0]
            return userid
 
    def remove_assignee(self, task_id, user_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "DELETE FROM assigned_to WHERE user_id=? AND task_id=?"
        pvalue = (user_id, task_id)
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(stmnt,pvalue)
            if cur.rowcount < 1:
                return False
            return True
 
    def assign_to_task(self, task_id, user_id):
        '''Assign user to task'''
         
        keys_on = 'PRAGMA foreign_keys = ON'
        check = "SELECT * FROM assigned_to WHERE user_id=? AND task_id=?"
        stmnt = "INSERT INTO assigned_to VALUES(?,?)"
 
        #If user is already assigned to task
        #Why did I wrote this??? Will SQLite raise an error anyway?
        # con = sqlite3.connect(self.db_path)
        # with con:
        #     con.row_factory = sqlite3.Row
        #     cur = con.cursor()
        #     cur.execute(keys_on)
        #     pvalue = (username,)
        #     cur.execute(stmnt, pvalue)
        #     row = cur.fetchone()
        #     if cur.rowcount is not None:
        #         return False
        #     con.close()
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (user_id, task_id)
            cur.execute(stmnt, pvalue)
            return True

    def get_assigned_users(self, task_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "SELECT user_id FROM assigned_to WHERE task_id=?"
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (task_id,)
            cur.execute(stmnt, pvalue)
            rows = cur.fetchall()
            if cur.rowcount is None:
                return False
            users = []
            for row in rows:
                user = dict(user=row[0])
                users.append(user)
            return users

    def add_comment(self, comment, task_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'INSERT INTO COMMENTS(comment, task_id) VALUES(?,?)'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (comment, task_id)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 0:
                return False
            return True

    def get_comments(self, task_id):
        '''Get all comments'''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'SELECT comment_id, comment, commented_date FROM comments WHERE task_id=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (task_id,)
            cur.execute(stmnt,pvalue)
            rows = cur.fetchall()
            if cur.rowcount is None:
                return False
            comments = []
            for row in rows:
                comment = dict(comment_id=row[0], comment=row[1], date=row[2])
                comments.append(comment)
            return comments
 
    def delete_comment(self, comment_id):
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "DELETE FROM comments WHERE comment_id=?"
        pvalue = (comment_id,)
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(stmnt,pvalue)
            if cur.rowcount < 1:
                return False
            return True
 
    def get_task(self, task_id):
        '''Get task'''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'SELECT * FROM tasks WHERE id=?'

        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (task_id,)
            cur.execute(stmnt,pvalue)
            row = cur.fetchone()
            if row is None:
                return False
            task = dict(task_id=row[0], title=row[1], category=row[2], description=row[3], priority=row[4], status=row[5], date=row[6])
            return task

    def get_tasks(self):
        '''Get all tasks'''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'SELECT * FROM tasks'
        con = sqlite3.connect(self.db_path)
        con.text_factory = str #To avoid UTF-8 encoding problem
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(stmnt)
            rows = cur.fetchall()
            if rows is None:
                return False
            tasks = []
            for row in rows:
                task = dict(task_id=row[0], title=row[1], category=row[2], description=row[3], priority=row[4], status=row[5], date=row[6])
                tasks.append(task)
            return tasks


    
    def update_priority(self, task_id, priority):
        keys_on = 'PRAGMA foreign_keys = ON'
        if priority not in [1, 2, 3, 4]:
            return False
        stmnt = 'UPDATE tasks SET priority=? WHERE id=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (priority,task_id)
            cur.execute(stmnt,pvalue)
            if cur.rowcount < 0:
                return False
            return True
        

    def remove_task(self, task_id):
        ##ON DELETE CASCADE NOT WORKING?
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'DELETE FROM tasks WHERE id=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (task_id,)
            cur.execute(stmnt,pvalue)
            if cur.rowcount < 1:
                return False
            return True

    def update_status(self, task_id, status):
        keys_on = 'PRAGMA foreign_keys = ON'
        if status not in [1, 2, 3, 4]:
            return False
        stmnt = 'UPDATE tasks SET status=? WHERE id=?'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (status, task_id)
            cur.execute(stmnt,pvalue)
            if cur.rowcount<1:
                return False
            return True

    def add_task(self, title, category, description, priority, status):
        keys_on = 'PRAGMA foreign_keys = ON'
        if status not in [1, 2, 3, 4]:
            return False
        elif priority not in [1, 2, 3, 4]:
            return False
        elif category not in ["frontend", "backend", "UX", "bug"]:
            return False
        stmnt = 'INSERT INTO TASKS(title, category, description, priority, status) VALUES(?,?,?,?,?)'
        #TODO: Add check for integrity error
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (title, category, description, priority, status)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return False
            return True

    # def modify_task(self, title, category, desc, assigned_to, priority, status):
    #
    #     pass
    #Added update_title, update_description, update_category separetely    -Nemo
