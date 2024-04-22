import os
import streamlit as st
import sqlite3
import google.generativeai as genai
import pandas as pd

# Assign the API key
api_key = 'AIzaSyCDIyaoZmxIFt0igAhQDB-FUk6HWc9vrHU'

# Configure Genai Key
genai.configure(api_key=api_key)

# Define Your Prompt
prompt = """
Before executing the queries, please carefully observe all the databases, tables, and column names.

You are an expert in converting English questions to SQL queries!

You are an expert in converting English questions to SQL query!
also the sql code should not have ``` in beginning or end and sql word in output

Show the total amount of male patients and the total amount of female patients in the patients table.
SELECT 
  (SELECT COUNT(*) FROM patients WHERE gender='M') AS male_count, 
  (SELECT COUNT(*) FROM patients WHERE gender='F') AS female_count;

Show first and last name, allergies from patients which have allergies to either 'Penicillin' or 'Morphine'. Show results ordered ascending by allergies then by first_name then by last_name.
SELECT
  first_name,
  last_name,
  allergies
FROM patients
WHERE
  allergies IN ('Penicillin', 'Morphine')
ORDER BY
  allergies,
  first_name,
  last_name;

Show patient_id and first_name from patients where their first_name start and ends with 's' and is at least 6 characters long.
SELECT
  patient_id,
  first_name
FROM patients
WHERE first_name LIKE 's__%s';

Show first name, last name and role of every person that is either patient or doctor.
The roles are either "Patient" or "Doctor"
SELECT first_name, last_name, 'Patient' as role FROM patients
    UNION ALL
SELECT first_name, last_name, 'Doctor' FROM doctors;

Show the total amount of male patients and the total amount of female patients in the patients table.
SELECT 
  (SELECT COUNT(*) FROM patients WHERE gender='M') AS male_count, 
  (SELECT COUNT(*) FROM patients WHERE gender='F') AS female_count;

Show first and last name, allergies from patients which have allergies to either 'Penicillin' or 'Morphine'. Show results ordered ascending by allergies then by first_name then by last_name.
SELECT
  first_name,
  last_name,
  allergies
FROM patients
WHERE
  allergies IN ('Penicillin', 'Morphine')
ORDER BY
  allergies,
  first_name,
  last_name;

Show patient_id and first_name from patients where their first_name starts and ends with 's' and is at least 6 characters long.
SELECT
  patient_id,
  first_name
FROM patients
WHERE first_name LIKE 's__%s';

Show first name, last name, and role of every person that is either patient or doctor.
The roles are either "Patient" or "Doctor".
SELECT first_name, last_name, 'Patient' as role FROM patients
    UNION ALL
SELECT first_name, last_name, 'Doctor' FROM doctors;

Show the total number of patients in the database.
SELECT COUNT(*) AS total_patients FROM patients;

Show the average age of male and female patients.
SELECT 
  AVG(age) AS avg_age_male
FROM patients 
WHERE gender = 'M'
UNION ALL
SELECT 
  AVG(age) AS avg_age_female
FROM patients 
WHERE gender = 'F';

Show the number of patients with each blood type.
SELECT 
  blood_type,
  COUNT(*) AS patient_count
FROM patients
GROUP BY blood_type;
"""

# Function To Load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    return response.text

# Function To retrieve query from the database and return as DataFrame
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# Function to display sample data for a table
def display_sample_data(table_name, db):
    st.subheader(f"Sample Data for Table: {table_name}")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} ", db)
        st.write(df)
    except Exception as e:
        st.error(f"Error retrieving sample data: {str(e)}")

# Function to insert data into a table
def insert_data_into_table(table_name, data, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO {table_name} VALUES {data}")
        conn.commit()
        st.success("Data inserted successfully!")
    except Exception as e:
        conn.rollback()
        st.error(f"Error inserting data: {str(e)}")
    finally:
        conn.close()

# Function to delete data from a table based on the value in the first column
def delete_data_from_table(table_name, column_name, value, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE {column_name}=?", (value,))
        conn.commit()
        st.success("Data deleted successfully!")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting data: {str(e)}")
    finally:
        conn.close()

# Function to create a new database
def create_database(database_name):
    conn = sqlite3.connect(database_name)
    conn.close()

# Function to create a new table
def create_table(table_name, columns, constraints, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE TABLE {table_name} ({', '.join([f'{col} {col_type} {constraint}' for col, (col_type, constraint) in columns.items()])} {', '.join(constraints)} )")
        conn.commit()
        st.success("Table created successfully!")
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating table: {str(e)}")
    finally:
        conn.close()

# Function to upload data from a CSV file into a table
def upload_csv_to_table(table_name, csv_file, db):
    try:
        df = pd.read_csv(csv_file)
        df.to_sql(table_name, sqlite3.connect(db), if_exists='append', index=False)
        st.success("Data uploaded successfully!")
    except Exception as e:
        st.error(f"Error uploading data: {str(e)}")

# Function to delete a database
def delete_database(database_name):
    try:
        os.remove(database_name)
        st.success("Database deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting database: {str(e)}")

# Function to delete a table
def delete_table(table_name, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        st.success("Table deleted successfully!")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting table: {str(e)}")
    finally:
        conn.close()

# Streamlit App
st.set_page_config(page_title="Gemini App To Retrieve SQL Data", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
st.title("Gemini SQL Assistant 🌟: Simplifying  Data Retrieval")

# Default content in the middle section
st.write("Welcome to Gemini SQL Assistant! Use the sidebar on the left to interact with the app.")

# Option to create a new database
create_database_option = st.sidebar.checkbox("Create New Database", key="create_db")

if create_database_option:
    database_name = st.sidebar.text_input("Enter Database Name:", key="db_name_input")
    if st.sidebar.button("Create Database", key="create_db_btn"):
        create_database(database_name)

# Option to select an existing database
database_list = [filename for filename in os.listdir() if filename.endswith('.db')]
database_name = st.sidebar.selectbox("Select Database", [''] + database_list, key="select_db") if database_list else None

# Connect to SQLite database
if database_name:
    if database_name != '':
        conn = sqlite3.connect(database_name)

        # Fetch list of tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]

        # Checkbox to show sample database
        show_sample_db = st.sidebar.checkbox("Show Sample Database", key="show_sample_db")

        if show_sample_db:
            # Display sample data for tables
            table_clicked = st.sidebar.selectbox("Select Table", tables, key="table_clicked")

            if table_clicked:
                display_sample_data(table_clicked, conn)

        # Heading for asking a question
        st.sidebar.header("Ask a Question")

        # Input field and button to ask the question
        question = st.sidebar.text_input("Input: ", key="input")
        # Increase width of input
        st.sidebar.markdown('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

        submit = st.sidebar.button("Ask the question", key="ask_question_btn")

        # if submit is clicked
        if submit:
            response = get_gemini_response(question, prompt)
            st.subheader("Generated SQL Query:")
            st.code(response, language='sql')  # Remove the 'key' parameter
            print("Generated SQL Query:", response)  # Debugging print

            try:
                result_df = read_sql_query(response, database_name)
                st.subheader("Database Query Response:")
                # Display DataFrame with wider format
                st.dataframe(result_df, width=None)
            except Exception as e:
                st.error(f"Error executing SQL query: {str(e)}")

        # Option to create a new table
        create_table_option = st.sidebar.checkbox("Create New Table", key="create_table")

        if create_table_option:
            table_name = st.sidebar.text_input("Enter Table Name:", key="table_name_input")
            num_columns = st.sidebar.number_input("Enter Number of Columns:", min_value=1, value=1, key="num_columns_input")
            columns = {}
            for i in range(num_columns):
                col_name = st.sidebar.text_input("Enter Column Name:", key=f"col_name_{i}")
                col_type = st.sidebar.selectbox("Select Column Type:", ["TEXT", "INTEGER", "REAL", "BLOB"], key=f"col_type_{i}")
                constraint = st.sidebar.selectbox("Select Constraint:", ["PRIMARY KEY", "NOT NULL", "UNIQUE", "DEFAULT"], key=f"constraint_{i}")
                columns[col_name] = (col_type, constraint)
            constraints = [f'{col_name} {constraint}' for col_name, (_, constraint) in columns.items() if constraint != "DEFAULT"]
            if st.sidebar.button("Create Table", key="create_table_btn"):
                create_table(table_name, columns, constraints, database_name)

        # Option to upload data from a CSV file
        upload_csv_option = st.sidebar.checkbox("Upload Data from CSV", key="upload_csv")

        if upload_csv_option:
            table_to_upload = st.sidebar.text_input("Enter Table Name for Uploaded Data:", key="upload_table_input")
            csv_file = st.sidebar.file_uploader("Upload CSV File", key="upload_csv_file")
            if csv_file is not None:
                if st.sidebar.button("Upload Data", key="upload_data_btn"):
                    upload_csv_to_table(table_to_upload, csv_file, database_name)

        # Option to insert data into a table
        insert_option = st.sidebar.checkbox("Insert Data into Table", key="insert_data")

        if insert_option:
            table_to_insert = st.sidebar.selectbox("Select Table to Insert Data", tables, key="select_insert_table")
            if table_to_insert:
                st.sidebar.subheader(f"Insert Data into Table: {table_to_insert}")
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_to_insert})")
                columns = [column[1] for column in cursor.fetchall()]
                data_to_insert = {}
                for column in columns:
                    data_to_insert[column] = st.sidebar.text_input(f"Enter value for {column}:", key=f"insert_data_{column}")
                if st.sidebar.button("Insert Data", key="insert_data_btn"):
                    data_tuple = tuple([data_to_insert[column] for column in columns])
                    insert_data_into_table(table_to_insert, data_tuple, database_name)
                    st.sidebar.success("Insertion completed!")

        # Option to delete data from a table
        delete_option = st.sidebar.checkbox("Delete Data from Table", key="delete_data")

        if delete_option:
            table_to_delete = st.sidebar.selectbox("Select Table to Delete Data", tables, key="select_delete_table")
            if table_to_delete:
                st.sidebar.subheader(f"Delete Data from Table: {table_to_delete}")
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_to_delete})")
                columns = [column[1] for column in cursor.fetchall()]
                column_to_delete = columns[0]  # Assuming the first column is used for deletion
                value_to_delete = st.sidebar.text_input(f"Enter value in {column_to_delete} to delete:", key="delete_value")
                if st.sidebar.button("Delete Data", key="delete_data_btn"):
                    delete_data_from_table(table_to_delete, column_to_delete, value_to_delete, database_name)

        # Option to delete the database
        delete_database_option = st.sidebar.checkbox("Delete Database", key="delete_db")

        if delete_database_option:
            if st.sidebar.button("Delete Database", key="delete_db_btn"):
                conn.close()  # Close the connection before attempting to delete the file
                delete_database(database_name)
                st.experimental_rerun()

        # Option to delete a table
        delete_table_option = st.sidebar.checkbox("Delete Table", key="delete_table")

        if delete_table_option:
            table_to_delete = st.sidebar.selectbox("Select Table to Delete", tables, key="select_delete_table")
            if table_to_delete:
                if st.sidebar.button("Delete Table", key="delete_table_btn"):
                    delete_table(table_to_delete, database_name)
                    st.experimental_rerun()

        # Close database connection
        conn.close()
