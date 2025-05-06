import mysql.connector
from config import DB_CONFIG


def execute_sql(sql_query: str):
    """This function connects to the MySQL database,
    executes the given SQL query, and returns the result.
    
    Args:
        sql_query (str): The SQL query to execute.
    
    Returns:
        tuple:(columns, rows)
            - columns: List of column names 
            - rows: List of tuples (each tuple = one row)
    """
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        

        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        else:

            affected_rows = cursor.rowcount
            columns = ["affected_rows"]
            rows = [(affected_rows,)]
        
        cursor.close()
        conn.close()
        
        return columns, rows
    
    except mysql.connector.Error as err:
        print(f"Error running query: {err}")
        return None, None