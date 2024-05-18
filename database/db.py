import psycopg2
import environ


# read variables for .env file
ENV = environ.Env()
environ.Env.read_env(".env")

class DB:

    def __init__(self):
        self.host = ENV.str("DB_HOST", "")
        self.user = ENV.str("DB_USER", "")
        self.password = ENV.str("DB_PASSWORD", "")
        self.database = ENV.str("DB_NAME", "")

    def connect(self):
        db = psycopg2.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            database=self.database
        )
        return db


class Customer:

    def __init__(self):
        self.conn = DB().connect()

    def add_customer(self, data):
        """
        first_name,
        last_name,
        phone_number
        """
        stmt = "INSERT INTO customer (user_name, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s)"

        cursor = self.conn.cursor()
        cursor.execute(stmt, data)
        self.conn.commit()

    def get_customer(self, data):
        stmt = "SELECT * FROM customer WHERE user_name=%s AND first_name = %s AND last_name = %s"
        cursor = self.conn.cursor()
        cursor.execute(stmt, data)
        record = cursor.fetchone()
        return record


class Meter:

    def __init__(self):
        self.conn = DB().connect()

    def add_meter(self, data):
        """
        customer_id, meter_number
        """
        stmt = "INSERT INTO meter (customer_id, meter_number) VALUES (%s, %s)"
        cursor = self.conn.cursor()
        cursor.execute(stmt, data)
        self.conn.commit()

    def remove_meter(self, data):
        """
        Set active to false for a particular meter
        """
        stmt = "UPDATE meter SET active = FALSE WHERE meter_number = (%s)"
        args = (data,)
        cursor = self.conn.cursor()
        cursor.execute(stmt, args)
        self.conn.commit()

    def get_meters(self, data):
        stmt = "SELECT meter_number FROM meter WHERE customer_id = (%s)"
        args = (data,)
        cursor = self.conn.cursor()
        cursor.execute(stmt, data)
        records = cursor.fetchall()
        return [x[0] for x in records]


# Meter().get_meters([14])
