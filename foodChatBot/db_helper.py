# Author: Dhaval Patel. Codebasics YouTube Channel
import mysql.connector

global cnx

# Establishing a global connection to MySQL database
cnx = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="PraNov@2002",
    database="eatery"
)


# Function to call the MySQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()

        # Assuming 'insert_order_item' is a stored procedure in MySQL
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1


# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    try:
        cursor = cnx.cursor()

        # Inserting the record into the order_tracking table
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print(f"Order tracking inserted successfully for order_id {order_id}")

    except mysql.connector.Error as err:
        print(f"Error inserting order tracking: {err}")

        # Rollback changes if necessary
        cnx.rollback()

    except Exception as e:
        print(f"An error occurred: {e}")

        # Rollback changes if necessary
        cnx.rollback()


# Function to get the total order price from the database
def get_total_order_price(order_id):
    try:
        cursor = cnx.cursor()

        # Executing the SQL query to get the total order price
        query = f"SELECT get_total_order_price({order_id})"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        return result

    except mysql.connector.Error as err:
        print(f"Error fetching total order price: {err}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Function to get the next available order_id
def get_next_order_id():
    try:
        cursor = cnx.cursor()

        # Executing the SQL query to get the next available order_id
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        # Returning the next available order_id
        if result is None:
            return 1
        else:
            return result + 1

    except mysql.connector.Error as err:
        print(f"Error fetching next order ID: {err}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Function to fetch the order status from the order_tracking table
# Function to fetch the order status from the order_tracking table
def get_order_status(order_id):
    try:
        if order_id is None:
            return None

        cursor = cnx.cursor()

        # Executing the SQL query to fetch the order status
        query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()

        # Closing the cursor
        cursor.close()

        # Returning the order status
        if result:
            return result[0]
        else:
            return None

    except mysql.connector.Error as err:
        print(f"Error fetching order status: {err}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    # Testing functions
    # print(get_total_order_price(56))
    # insert_order_item('Samosa', 3, 99)
    # insert_order_item('Pav Bhaji', 1, 99)
    # insert_order_tracking(99, "in progress")
    print(get_next_order_id())

