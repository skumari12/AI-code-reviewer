import mysql.connector


def get_db_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="947030",
        database="ai_code_reviewer"
    )

    return connection