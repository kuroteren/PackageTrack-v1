# Alexander Hess
# CS370

# PackageTrack

# Import sqlite
import sqlite3

class SqlConnect:
    def __init__(self):
        self.eflag = False
        self.error = None
        self.db = None

    def create(self):
        if self.db is not None:
            ########################
            # id --------------> 0 #
            # carroer ---------> 1 #
            # tracking_numner -> 2 #
            # status ----------> 3 #
            # notified --------> 4 #
            ########################
            sql_create_prime_table = """ CREATE TABLE IF NOT EXISTS Orders (
                                        id integer PRIMARY KEY,
                                        carrier text NOT NULL,
                                        tracking_number text NOT NULL,
                                        status text,
                                        notified integer
                                        ); """

            c = self.db.cursor()

            c.execute(sql_create_prime_table)

    def add_package(self, *data):
        # Query
        sql = ''' INSERT INTO Orders(carrier, tracking_number, notified)
                    VALUES(?,?,0) '''

        # Execution
        c = self.db.cursor()
        c.execute(sql, data)
        self.db.commit()

    # Search packages
    def search_orders(self, data):
        formatted = str('%' + data + '%')
        # Execution
        c = self.db.cursor()
        c.execute("SELECT * FROM Orders WHERE tracking_number LIKE ?", (formatted,))

        res = c.fetchall()

        return res

    def get_orders(self):
        # Execution
        c = self.db.cursor()
        c.execute("SELECT * FROM Orders")

        result = c.fetchall()

        return result

    def count_orders(self):
        # Query
        sql = ''' SELECT COUNT( id ) FROM Orders '''

        self.connect()
        c = self.db.cursor()
        c.execute(sql)

        return str(c.fetchone()[0])

    # Update status of package
    # Order of data:
    #   status, tracking_number
    def update_status(self, *data):
        # Query
        sql = ''' UPDATE Orders 
                    SET status = ?
                    WHERE tracking_number = ? '''

        self.connect()
        # Execution
        c = self.db.cursor()
        c.execute(sql, data)
        self.db.commit()

    def set_notified(self, data):
        # Query
        sql = ''' UPDATE Orders
                    SET notified = 1
                    WHERE tracking_number = ?'''

        self.connect()
        # Execution
        c = self.db.cursor()
        c.execute(sql, (data, ))
        self.db.commit()

    # Delete package from database by tracking number
    def delete_package(self, data):
        sql = ''' DELETE FROM Orders WHERE tracking_number = ?'''

        self.connect()
        # Execution
        c = self.db.cursor()
        c.execute(sql, data)
        self.db.commit()

    def close(self):
        self.db.close()

    def connect(self):
        try:
            self.db = sqlite3.connect("db")
            self.create()
        except sqlite3.Error as e:
            # If it errors, program will close
            self.error = e
            self.eflag = True


# # # # # # # # # #
# End of Database #
# # # # # # # # # #
