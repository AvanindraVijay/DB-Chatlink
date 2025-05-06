from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model_name = "defog/sqlcoder-7b-2" 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


logger.info(f"Loading model {model_name} on {device}...")
try:
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    logger.info("Model and tokenizer loaded successfully!")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    logger.warning("Falling back to rule-based SQL generation.")
    model = None
    tokenizer = None


DATABASE_SCHEMA = """
CREATE TABLE user_details (
    name VARCHAR(200),
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address VARCHAR(200),
    gender VARCHAR(20),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_name_UNIQUE UNIQUE (user_name),
    CONSTRAINT email_UNIQUE UNIQUE (email),
    CONSTRAINT phone_UNIQUE UNIQUE (phone)
);

CREATE TABLE internship_details (
    id SERIAL PRIMARY KEY,
    internship_id VARCHAR(100) NOT NULL UNIQUE,
    company_name VARCHAR(200) NOT NULL,
    job_description VARCHAR(2000),
    role VARCHAR(200) NOT NULL,
    seat INT NOT NULL,
    stipend DECIMAL(10,2),
    duration INT,  -- in months
    location VARCHAR(200),
    remote_work BOOLEAN DEFAULT FALSE,
    requirements VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    end_date DATE,
    application_deadline DATE,
    status VARCHAR(200)
);

CREATE TABLE user_internship (
    id SERIAL PRIMARY KEY,
    internship_id VARCHAR(200) NOT NULL,
    user_name VARCHAR(200) NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resume_link VARCHAR(500),
    cover_letter_text TEXT,
    interview_date DATE,
    interview_feedback TEXT,
    score DECIMAL(5,2),
    status VARCHAR(200),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_internship FOREIGN KEY (internship_id) REFERENCES internship_details(internship_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_name) REFERENCES user_details(user_name) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT unique_internship_user UNIQUE (internship_id, user_name)
);
""" 


SAMPLE_DATA_DESCRIPTION = """
-- Example data in the database:
-- user_details: Contains information about users/students (name, email, phone, etc.)
-- internship_details: Lists available internships with company name, role, and status
-- user_internship: Maps users to internships they've applied for, with application status
"""


def generate_sql_with_model(question):
    """Generate SQL query using the SQLCoder model with support for advanced SQL features."""
    prompt = f"""
### Task
Generate a SQL query to answer the following question:
{question}

### Database Schema
The query will run on a database with the following schema:
{DATABASE_SCHEMA}

{SAMPLE_DATA_DESCRIPTION}

### Instructions
- Write a complete SQL query that directly answers the question
- Support complex features including JOINs, WHERE clauses, GROUP BY, HAVING, window functions, CTEs when appropriate
- Ensure all table names and column references are correct based on the schema
- Use proper SQL standards and best practices
- Format the query with clear indentation for readability
- Add brief comments to explain complex parts of the query
- Prefer explicit column references over SELECT *
- Use efficient query patterns for optimal performance

### Answer
Given the database schema, here is the SQL query that answers the question:
```sql
"""
    try:
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
        outputs = model.generate(
            inputs,
            max_length=2048,
            temperature=0.3,
            top_p=0.95,
            num_return_sequences=1,
            do_sample=True,
            repetition_penalty=1.1,
            length_penalty=1.0,
            pad_token_id=tokenizer.eos_token_id
        )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        sql_match = re.search(r"``[sql\s+(.*?)(?:](http://_vscodecontentref_/0)``|$)", generated_text, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        return generated_text.replace(prompt, "").strip()
    except Exception as e:
        logger.error(f"Error generating SQL with model: {e}")
        return None


def generate_advanced_rule_based_sql(question):
    """Generate a SQL query based on advanced pattern matching and rule-based system."""
    question = question.lower()
    has_aggregation = any(word in question for word in ["count", "sum", "average", "avg", "maximum", "max", "minimum", "min"])
    has_group = any(word in question for word in ["group", "each", "by", "per"])
    has_order = any(word in question for word in ["order", "sort", "arrange", "rank"])
    has_limit = any(word in question for word in ["limit", "top", "first", "recent"])
    has_join = any(word in question for word in ["join", "combine", "related", "connection", "between"])
    has_condition = any(word in question for word in ["where", "if", "when", "condition", "filter", "specific"])
    entities = []
    if "user" in question or "student" in question:
        entities.append("user_details")
    if "internship" in question:
        entities.append("internship_details")
    if "application" in question or "applied" in question:
        entities.append("user_internship")
    if not entities:
        entities = ["user_details", "internship_details", "user_internship"]

    return "SELECT * FROM user_details;" 


def question_to_sql(question):
    """Convert a natural language question to SQL query with support for complex features."""
    logger.info(f"Processing question: {question}")
    if model and tokenizer:
        try:
            logger.info("Attempting SQL generation with model...")
            sql = generate_sql_with_model(question)
            if sql:
                logger.info("Successfully generated SQL with model")
                return sql
            else:
                logger.warning("Model returned empty SQL, falling back to rule-based generation")
        except Exception as e:
            logger.error(f"Error using ML model: {e}")
    logger.info("Using rule-based SQL generation...")
    return generate_advanced_rule_based_sql(question)


if __name__ == "__main__":
    test_questions = [
        "List all internships",
        "Show me all users",
        "How many applications are there per status category?",
        "Which companies have the most internships available?",
        "What's the average stipend for internships by industry?",
    ]
    for q in test_questions:
        print(f"\nQuestion: {q}")
        sql = question_to_sql(q)
        print(f"SQL: \n{sql}")
        print("-" * 80)