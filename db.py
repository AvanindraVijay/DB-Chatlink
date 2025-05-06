import mysql.connector
from config import DB_CONFIG
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_user_details(user_name):
    """Fetch detailed information about a user including internship statistics.
    
    Args:
        user_name: Username to fetch details for
        
    Returns:
        tuple: (name, total_internships, companies, company_list, selected, rejected)
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get basic user info
        user_query = """
        SELECT name FROM user_details WHERE user_name = %s
        """
        cursor.execute(user_query, (user_name,))
        user_result = cursor.fetchone()
        
        if not user_result:
            logger.warning(f"No user found with username: {user_name}")
            return None
        
        name = user_result[0]
        

        stats_query = """
        SELECT 
            COUNT(DISTINCT ui.internship_id) as total_internships,
            COUNT(DISTINCT id.company_name) as companies,
            GROUP_CONCAT(DISTINCT id.company_name SEPARATOR ', ') as company_list,
            (SELECT GROUP_CONCAT(DISTINCT id2.company_name SEPARATOR ', ')
                FROM user_internship ui2
                JOIN internship_details id2 ON ui2.internship_id = id2.internship_id
                WHERE ui2.user_name = %s AND ui2.status = 'selected') as selected,
            (SELECT GROUP_CONCAT(DISTINCT id3.company_name SEPARATOR ', ')
                FROM user_internship ui3
                JOIN internship_details id3 ON ui3.internship_id = id3.internship_id
                WHERE ui3.user_name = %s AND ui3.status = 'rejected') as rejected
        FROM user_internship ui
        JOIN internship_details id ON ui.internship_id = id.internship_id
        WHERE ui.user_name = %s
        """
        
        cursor.execute(stats_query, (user_name, user_name, user_name))
        stats_result = cursor.fetchone()
        
        if not stats_result:
            total_internships = 0
            companies = 0
            company_list = "None"
            selected = None
            rejected = None
        else:
            total_internships, companies, company_list, selected, rejected = stats_result
            
        cursor.close()
        conn.close()
        
        return (name, total_internships, companies, company_list, selected, rejected)
    
    except mysql.connector.Error as err:
        logger.error(f"Database error fetching user details: {err}")
        return None
    except Exception as e:
        logger.error(f"Error in fetch_user_details: {e}")
        return None

def execute_custom_query(query, params=None):
    """Execute a custom database query with optional parameters.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters for parameterized queries
        
    Returns:
        tuple: (columns, rows) - Column names and result rows
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        else:
            columns = ["affected_rows"]
            rows = [(cursor.rowcount,)]
        
        cursor.close()
        conn.close()
        
        return columns, rows
    
    except mysql.connector.Error as err:
        logger.error(f"Database error executing custom query: {err}")
        return None, None