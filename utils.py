from pythonping import ping
from re import match
import sqlite3 as sql

# utilitary function to execute a saving query to the db
def _save_to_db(QUERY: str, params : tuple):
    with sql.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(QUERY, params)

        try:
            connection.commit()
            return True
        except:
            connection.rollback()
            return False
# utilitary function to execute a query which pulls from the DB
def _pull_from_db(QUERY : str, params : tuple = ()):
    with sql.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(QUERY, params)
        return cursor.fetchall()


# checks if an ip has the right format
def _check_address_format(address):
    if match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", address):
            return True
    return False

# decorator used to ensure an address has the right format
# made to avoid having to write an if in each function
def _check_address(func):
        def wrapper(address, display_name):
            if _check_address_format(address):
                return func(address, display_name)
            else:
                return False
        return wrapper



# DB entries are formatted as : (id, display_name, address)
def get_list_status():
    ip_status_list = [[1, 1]]

    address_list = _pull_from_db("SELECT * FROM targets")

    for address in address_list:
        # send the ping and gets the avalaibilty
        ping_result = ping(address[2], count=1)
        is_avalaible = (1 if ping_result.success() else 0)
        #sets up a row as : [address, display_name, avalaibility, average_ping]
        ip_status_list.append([address[2], address[1], is_avalaible, ping_result.rtt_avg_ms])

    return ip_status_list

# add form back-end logic
@_check_address
def add_ip(address, display_name = "Cible"):
    # sets a default display name
    if len(display_name) == 0:
        display_name = "Cible"
    _save_to_db("INSERT INTO targets (address, display_name) VALUES (?,?)", (address, display_name))

# remove form back-end logic
@_check_address
def remove_ip(address = None, display_name = None):
    # makes deletion only avalaible for either display name or address 
    if display_name:
        _save_to_db("DELETE FROM targets WHERE display_name = ?", (display_name,))
        return True
    else:
        _save_to_db("DELETE FROM targets WHERE address = ?", (address,))
        return True
