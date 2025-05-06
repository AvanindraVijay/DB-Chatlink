from db import fetch_user_details
import os
import re
from typing import List, Tuple, Any, Dict
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def format_value(value: Any) -> str:
    """Format values appropriately for natural language responses.
    
    Args:
        value: Any data value from SQL query results
        
    Returns:
        str: Formatted value as string
    """
    if value is None:
        return "None"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return value
    else:
        return str(value)

def identify_query_type(question: str, columns: List[str], rows: List[Tuple]) -> str:
    """Identify the type of query to help generate appropriate responses.
    
    Args:
        question: Original user question
        columns: Column names from the query result
        rows: Data rows from the query result
        
    Returns:
        str: Query type identifier
    """
    question = question.lower()
    

    if "count" in question or "how many" in question:
        if len(columns) == 1 and len(rows) == 1:
            return "count"
    

    if len(rows) == 1:
        return "single_entity"
    

    if "list" in question or "show" in question or "all" in question:
        return "list"
    

    if any(col.lower().startswith(("avg", "sum", "max", "min")) for col in columns):
        return "aggregation"
    

    if len(rows) > 1:
        return "list"
    
    return "general"

def extract_entity_name(question: str) -> str:
    """Extract the main entity being queried about.
    
    Args:
        question: Original user question
        
    Returns:
        str: Entity name (users, internships, applications)
    """
    question = question.lower()
    
    if "user" in question or "student" in question:
        return "users"
    elif "internship" in question or "job" in question:
        return "internships"
    elif "application" in question or "applied" in question:
        return "applications"
    else:
        return "items"

def format_tabular_data(columns: List[str], rows: List[Tuple], limit: int = 10) -> str:
    """Format data as a textual table for better readability.
    
    Args:
        columns: Column names from the query result
        rows: Data rows from the query result
        limit: Maximum number of rows to display
        
    Returns:
        str: Formatted table as text
    """
    if not rows:
        return "No data found."
    

    col_widths = [len(col) for col in columns]
    for row in rows[:limit]:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(format_value(val)))
    

    header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
    separator = "-" * len(header)
    

    formatted_rows = []
    for row in rows[:limit]:
        formatted_row = " | ".join(format_value(val).ljust(col_widths[i]) for i, val in enumerate(row))
        formatted_rows.append(formatted_row)
    

    if len(rows) > limit:
        formatted_rows.append(f"... and {len(rows) - limit} more rows")
    

    return f"{header}\n{separator}\n" + "\n".join(formatted_rows)

def generate_count_response(question: str, columns: List[str], rows: List[Tuple]) -> str:
    """Generate response for count queries.
    
    Args:
        question: Original user question
        columns: Column names from the query result
        rows: Data rows from the query result
        
    Returns:
        str: Natural language response
    """
    entity = extract_entity_name(question)
    count = rows[0][0]
    

    if count == 0:
        return f"I found no {entity} matching your criteria."
    elif count == 1:
        return f"There is 1 {entity[:-1]} matching your criteria."
    else:
        return f"There are {count} {entity} matching your criteria."

def generate_list_response(question: str, columns: List[str], rows: List[Tuple]) -> str:
    """Generate response for list queries.
    
    Args:
        question: Original user question
        columns: Column names from the query result
        rows: Data rows from the query result
        
    Returns:
        str: Natural language response
    """
    entity = extract_entity_name(question)
    
    if len(rows) == 0:
        return f"I couldn't find any {entity} matching your criteria."
    
    intro = f"Here are the {len(rows)} {entity} I found:"
    table = format_tabular_data(columns, rows)
    
    return f"{intro}\n\n{table}"

def generate_single_entity_response(question: str, columns: List[str], rows: List[Tuple]) -> str:
    """Generate response for single entity queries.
    
    Args:
        question: Original user question
        columns: Column names from the query result
        rows: Data rows from the query result
        
    Returns:
        str: Natural language response
    """
    entity = extract_entity_name(question)[:-1]  
    
    result = rows[0]
    details = []
    
    for i, col in enumerate(columns):
        formatted_col = col.replace('_', ' ').title()
        details.append(f"{formatted_col}: {format_value(result[i])}")
    
    return f"Here are the details for the {entity}:\n\n" + "\n".join(details)

def generate_aggregation_response(question: str, columns: List[str], rows: List[Tuple]) -> str:
    """Generate response for aggregation queries.
    
    Args:
        question: Original user question
        columns: Column names from the query result
        rows: Data rows from the query result
        
    Returns:
        str: Natural language response
    """

    entity = extract_entity_name(question)
    
    intro = f"Here's the requested summary information about {entity}:"
    table = format_tabular_data(columns, rows)
    
    return f"{intro}\n\n{table}"

def handle_user_details_query(user_name: str) -> str:
    """Handle specific query about user details.
    
    Args:
        user_name: Username to fetch details for
        
    Returns:
        str: Natural language response with user details
    """
    user_info = fetch_user_details(user_name)
    
    if not user_info:
        return f"No record found for {user_name}"
        
    name, total_internships, companies, company_list, selected, rejected = user_info
    

    selected = selected if selected else "None"
    rejected = rejected if rejected else "None"
    
    return f"""
    Name: {name}
    Applied in {total_internships} internships across {companies} companies: {company_list}
    Selected in: {selected}
    Rejected in: {rejected}
    """

def generate_general_response(question: str, columns: List[str], rows: List[Tuple]) -> str:
    """Generate a general response when no specific pattern is detected.
    
    Args:
        question: Original user question
        columns: Column names from the query result
        rows: Data rows from the query result
        
    Returns:
        str: Natural language response
    """
    intro = "Here are the results for your query:"
    table = format_tabular_data(columns, rows)
    
    return f"{intro}\n\n{table}"

def generate_response(question: str, columns: List[str], rows: List[Tuple]) -> str:
    """Generate a natural language response based on SQL query results.
    
    Args:
        question: Original user question
        columns: Column names from the query result
        rows: Data rows from the query result
        
    Returns:
        str: Natural language response
    """
    logger.info(f"Generating response for question: {question}")
    

    if "details of" in question.lower():

        parts = question.lower().split("details of")
        if len(parts) > 1:
            user_name = parts[1].strip()
            return handle_user_details_query(user_name)
    

    query_type = identify_query_type(question, columns, rows)
    logger.info(f"Identified query type: {query_type}")
    
    if query_type == "count":
        return generate_count_response(question, columns, rows)
    elif query_type == "list":
        return generate_list_response(question, columns, rows)
    elif query_type == "single_entity":
        return generate_single_entity_response(question, columns, rows)
    elif query_type == "aggregation":
        return generate_aggregation_response(question, columns, rows)
    else:
        return generate_general_response(question, columns, rows)


if __name__ == "__main__":

    test_questions = [
        "How many users are there?",
        "List all internships",
        "Show me details of user john_doe",
        "What is the average stipend for internships?",
        "Give me information about the Computer Science internship"
    ]
    
    test_data = [
        (["count(*)"], [(42,)]),
        (["id", "company_name", "role", "stipend"], [(1, "Tech Corp", "Software Engineer", 5000), (2, "Data Inc", "Data Analyst", 4500), (3, "AI Labs", "ML Engineer", 6000)]), (["name", "email", "phone", "address"], 
        [("John Smith", "john@example.com", "123-456-7890", "123 Main St")]),
        (["avg(stipend)"], [(5166.67,)]),
        (["id", "internship_id", "company_name", "role", "stipend"], [(5, "CS001", "Tech University", "Research Assistant", 3000)])
    ]
    
    for i, question in enumerate(test_questions):
        cols, rows = test_data[i % len(test_data)]
        print(f"\nQuestion: {question}")
        response = generate_response(question, cols, rows)
        print(f"Response:\n{response}")
        print("-" * 80)