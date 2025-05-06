from sql_defog import question_to_sql
from sql_executor import execute_sql
from nl_response_generator import generate_response

def main():
    print("Welcome to the SQL Chatbot!")
    print("Note: Using simplified response generation (no LLM for responses)")
    
    while True:
        user_question = input("\nWhat do you want to ask? (type 'exit' to quit)\n> ")
        
        if user_question.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        
        try:
            sql_query = question_to_sql(user_question)
            print("\nGenerated SQL Query:")
            print(sql_query)
            
            columns, rows = execute_sql(sql_query)
            
            if not columns or not rows:
                print("\nNo data found for the given query.")
                continue
            
            natural_response = generate_response(user_question, columns, rows)
            
            print("\nAI Response:")
            print(natural_response)
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again with a different question.")

if __name__ == "__main__":
    main()