import mysql.connector


def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kattasyamala@19",
        database="kyc_monitor"
    )

    return connection


if __name__ == "__main__":

    try:

        connection = get_connection()

        if connection.is_connected():

            print(
                "MySQL Database Connected Successfully!"
            )

        connection.close()

    except mysql.connector.Error as error:

        print(
            "Database Connection Error:",
            error
        )