from sqlalchemy import create_engine, inspect, text
import json
from colorama import Fore, Style, init
from flask import Flask, request, jsonify
from better_profanity import profanity
import google.generativeai as genai
import psycopg2
import logging
import re

app = Flask(__name__)
init(autoreset=True)
profanity.load_censor_words()

api_key = "" 

client = genai.configure(api_key=api_key)
schema = ""
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Database Connection Configuration
DATABASE_URI = ""
engine = ""
inspector = ""



def moderate_input(user_input):

    if profanity.contains_profanity(user_input):
        return False, "Please avoid using inappropriate language and rephrase your query."
    return True, None

def get_schema_metadata(engine):
    
    schema_metadata = {}
    relationships = {}

    
    for table_name in inspector.get_table_names():
        # Get columns
        columns = inspector.get_columns(table_name)
        schema_metadata[table_name] = [
            {"column_name": col["name"], "data_type": col["type"]} for col in columns
        ]

        foreign_keys = inspector.get_foreign_keys(table_name)
        for fk in foreign_keys:
            referred_table = fk["referred_table"]
            local_column = fk["constrained_columns"][0]
            referred_column = fk["referred_columns"][0]

            if table_name not in relationships:
                relationships[table_name] = []
            relationships[table_name].append({
                "referred_table": referred_table,
                "local_column": local_column,
                "referred_column": referred_column,
            })

    return schema_metadata, relationships

def format_schema_for_prompt(schema_metadata, relationships):
    schema_info = []
    print(f"SCHEMA: {schema_metadata}")
    for table, columns in schema_metadata.items():
        formatted_columns = ", ".join(
        [f"{col['column_name']} {col['data_type'].split('(')[0]}," for col in columns])
        schema_info.append(f"{table} {formatted_columns}[SEP]")

        if table in relationships:
            for rel in relationships[table]:
                schema_info.append(
                    f"{table}.{rel['local_column']} references {rel['referred_table']}.{rel['referred_column']}"
                )
    return "\n".join(schema_info)

def generate_sql_query(user_input, schema):


    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Convert the following request into an SQL query:
    Request: "{user_input}"
    SQL Schema: {schema}
    SQL Query:
    """
    response = model.generate_content(prompt)
    response = response.text
    logging.debug(f"RAW {response}")
    return response

def execute_sql(query):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            column_names = list(result.keys())
            result_dict = []
            
            for row in rows:
                row_dict = {column_names[i]: row[i] for i in range(len(row))}
                result_dict.append(row_dict)
            
            return result_dict
    except Exception as e:
        return f"Error executing query: {e}"
    
def get_schema():
    try:
        with engine.connect() as connection:
            # Fetch all table names
            result = connection.execute(text(("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")))
            tables = result.fetchall()
            #print(f"TABLES {tables}")
            schema = {
                "tables": []
            }
            
            # Fetch columns for each table
            for table in tables:
                #print(f"TABLE {table}")
                table_name = table[0]
                table_info = {
                    "table_name": table_name,
                    "columns": []
                }
                #print(f"TABLE NAME {table_name}")
                result_col = connection.execute(text((f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")))
                columns = result_col.fetchall()
                #print(f"Columns: {columns}")

                for column in columns:
                    column_name, data_type = column
                    column_info = {
                        "column_name": column_name,
                        "data_type": data_type
                    }
                    table_info["columns"].append(column_info)

                schema["tables"].append(table_info)

            return schema
    except Exception as e:
        return f"Error executing query: {e}"

# Create schema string in the format expected by the model
def create_schema_string(schema):
    schema_json = json.dumps(schema, indent=4)
    return schema_json

def generate_ddl():
    all_ddls = ""
    for table_name in inspector.get_table_names():
        # Get columns
        columns = inspector.get_columns(table_name)
        column_defs = []
        
        for column in columns:
            column_def = f"{column['name']} {column['type']}"
            
            # Add 'NOT NULL' constraint if necessary
            if not column.get('nullable', True):
                column_def += " NOT NULL"
            
            # Add 'PRIMARY KEY' constraint if applicable
            if column['name'] in inspector.get_pk_constraint(table_name).get('constrained_columns', []):
                column_def += " PRIMARY KEY"
            
            column_defs.append(column_def)

        # Get foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        for fk in foreign_keys:
            for constrained_col, referred_table, referred_col in zip(fk['constrained_columns'], fk['referred_table'], fk['referred_columns']):
                column_defs.append(f"FOREIGN KEY ({constrained_col}) REFERENCES {referred_table}({referred_col})")

        # Generate final DDL
        ddl = f"CREATE TABLE {table_name} (\n"
        ddl += ",\n".join(column_defs)
        ddl += "\n);"
        all_ddls += ddl +"\n\n"
    return all_ddls

def extract_sql(text):
    pattern = r"```sql\s*(.*?)\s*```"
    matches = re.findall(pattern, text, re.DOTALL)
    for i, match in enumerate(matches, start=1): 
        query = match.strip()  
    
    return query


@app.before_request
def initialize_schema():
    global schema, DATABASE_URI, engine, inspector

    DATABASE_URI=""
    engine = create_engine(DATABASE_URI)
    inspector = inspect(engine)
    
    schema = generate_ddl()
    logging.debug(f"SCHEMA {schema}")

@app.route('/query', methods=['POST'])
def text_to_sql():
        
    data = request.json
    user_input = data.get('query', '')

    # Check for abusive language
    is_valid, message = moderate_input(user_input)
    if not is_valid:
        return jsonify({"error": message}), 400

    try:
        sql_query = extract_sql(generate_sql_query(user_input, schema))
        logging.debug(f"SQL {sql_query}")

        if sql_query is not None:
            results = execute_sql(sql_query)
            if len(results) == 0:
                results = "There is no data for this query"
            return jsonify({"query": sql_query, "results": results}), 200
        else:
            raise Exception("Could not generate sql")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

