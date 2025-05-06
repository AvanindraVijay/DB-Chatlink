# SQL Chatbot: Natural Language to SQL Query System

![SQL Chatbot Banner](https://via.placeholder.com/1200x300?text=SQL+Chatbot)

A conversational interface for database interactions that translates natural language questions into SQL queries, executes them, and returns responses in plain English.

## 🌟 Features

- **Natural Language Understanding**: Ask questions in plain English about your data
- **SQL Generation**: Automatically converts natural language to optimized SQL queries
- **Intelligent Responses**: Formats SQL results into clear, human-readable responses
- **Hybrid Approach**: Uses both ML and rule-based systems for query generation
- **Database Agnostic**: Works with any MySQL-compatible database

## 📋 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Sample Questions](#-sample-questions)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Prerequisites

- Python 3.7+
- MySQL database
- At least 8GB RAM (for ML model)

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/sql-chatbot.git
cd sql-chatbot
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Configure your database connection in `config.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'internship_db'  # Your database name
}
```

2. Database Schema Setup:
   - The system works with a specific database schema focused on internships, users, and applications
   - Execute the SQL script in `schema/setup.sql` to create the required tables

```bash
mysql -u your_username -p your_database < schema/setup.sql
```

## 🖥️ Usage

Run the main script to start the chatbot interface:

```bash
python main.py
```

Example interaction:
```
Welcome to the SQL Chatbot!
Note: Using simplified response generation (no LLM for responses)

What do you want to ask? (type 'exit' to quit)
> List all internships from Google

Generated SQL Query:
SELECT internship_id, company_name, role, stipend, location, application_deadline 
FROM internship_details 
WHERE company_name = 'Google';

AI Response:
Here are the 3 internships I found:

internship_id | company_name | role                 | stipend  | location     | application_deadline
--------------|-------------|----------------------|----------|-------------|---------------------
GOOGL001      | Google      | Software Engineer    | 8000.00  | Mountain View| 2025-06-30
GOOGL002      | Google      | UX Designer          | 7500.00  | New York     | 2025-06-15
GOOGL003      | Google      | Data Scientist       | 8200.00  | Remote       | 2025-07-01
```

## 📁 Project Structure

```
sql-chatbot/
├── main.py                    # Entry point and UI
├── sql_defog.py               # Natural language to SQL conversion
├── sql_executor.py            # SQL query execution
├── nl_response_generator.py   # Natural language response generation
├── db.py                      # Direct database access functions
├── config.py                  # Configuration settings
├── schema/
│   └── setup.sql              # Database schema setup
├── requirements.txt           # Project dependencies
└── README.md                  # This file
```

## 🔄 How It Works

1. **Question Input**: User enters a natural language question
2. **NL to SQL**: The question is processed to generate an SQL query
   - Uses a pre-trained language model (`defog/sqlcoder-7b-2`)
   - Falls back to rule-based generation if model isn't available
3. **Query Execution**: SQL query is executed against the database
4. **Response Generation**: Results are formatted into natural language
   - Identifies query type (count, list, single entity, etc.)
   - Formats data appropriately (tables, summaries, etc.)
5. **Output**: Presents both the SQL and natural language response to the user

## 💬 Sample Questions

Try asking questions like:

- "List all internships at Google"
- "How many internships are available?"
- "What's the average stipend for software engineering roles?"
- "Show me details of user john_doe"
- "Count applications by status"
- "Which company offers the highest paying internship?"
- "List internships with application deadlines next month"
- "Show me all remote internships"

## ❓ Troubleshooting

### Model Loading Issues

If you encounter errors loading the model:

```
Error loading model: No module named 'transformers'
Falling back to rule-based SQL generation.
```

Ensure you have installed all requirements and have sufficient RAM.

### Database Connection Errors

```
Error running query: Access denied for user 'root'@'localhost'
```

Verify your database credentials in `config.py` and ensure your MySQL server is running.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔮 Future Enhancements

- [ ] Support for more database types (PostgreSQL, SQLite)
- [ ] Web interface with query history
- [ ] Query visualization features
- [ ] More sophisticated response generation
- [ ] User feedback mechanism to improve accuracy

---

Made with ❤️ by [Your Name]
