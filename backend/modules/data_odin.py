import sqlite3

class DB:
    def __init__(self):
        self.conn = sqlite3.connect('car_database.db', check_same_thread=False)

    def init(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS cars 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         plate_number TEXT NOT NULL UNIQUE, 
                         owner_name TEXT NOT NULL, 
                         car_model TEXT NOT NULL, 
                         car_color TEXT NOT NULL, 
                         balance REAL DEFAULT 0, 
                         stolen BOOLEAN DEFAULT 0,
                         exempted BOOLEAN DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS car_logs 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     car_id INTEGER NOT NULL, 
                     event_type TEXT NOT NULL, 
                     event_description TEXT, 
                     event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                     toll_booth TEXT, 
                     FOREIGN KEY(car_id) REFERENCES cars(id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     username TEXT NOT NULL UNIQUE, 
                     password TEXT NOT NULL,
                     token TEXT)''')
        self.conn.commit()
        try:
            c.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                      ("administrator", "adminPassword"))
            c.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                      ("DARB", "DARB-plaza"))
            c.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                      ("SALIK", "SALIK-plaza"))
            self.conn.commit()
        except:
            pass
        return c

    def commit(self):
        self.conn.commit()