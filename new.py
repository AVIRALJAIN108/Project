import os
import streamlit as st
import sqlite3
import google.generativeai as genai
import pandas as pd
from emoji import emojize

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
        # Construct a parameterized query
        query = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(data))})"
        cursor.execute(query, data)
        conn.commit()
        st.success(emojize("Data inserted successfully! :thumbs_up:"))
        st.write(emojize(":rocket: Woohoo! Data has been successfully inserted."))
    except Exception as e:
        conn.rollback()
        st.error(f"Error inserting data: {str(e)}")
        st.write(emojize(":warning: Oops! Something went wrong while inserting data."))

# Function to delete data from a table
def delete_data_from_table(table_name, column_name, value, db, password):
    if password == "AviralJain@12":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE {column_name}=?", (value,))
            conn.commit()
            st.success(emojize("Data deleted successfully! :wastebasket:"))
            st.write(emojize(":raised_hands: Hooray! Data has been successfully deleted."))
        except Exception as e:
            conn.rollback()
            st.error(f"Error deleting data: {str(e)}")
            st.write(emojize(":x: Oops! Something went wrong while deleting data."))
        finally:
            conn.close()
    else:
        st.error("Incorrect password! Access denied.")
        st.write(emojize(":lock: Oops! Incorrect password. Access denied."))

# Function to create a new database
def create_database(database_name):
    conn = sqlite3.connect(database_name)
    conn.close()
    st.success(emojize("Database created successfully! :floppy_disk:"))
    st.write(emojize(":tada: Yay! Database has been successfully created."))

# Function to create a new table
def create_table(table_name, columns, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        # Constructing the CREATE TABLE statement
        columns_str = ', '.join([f'{col} {col_type}' for col, col_type in columns.items()])
        cursor.execute(f"CREATE TABLE {table_name} ({columns_str})")
        conn.commit()
        st.success(emojize("Table created successfully! :white_check_mark:"))
        st.write(emojize(":partying_face: Hurray! Table has been successfully created."))
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating table: {str(e)}")
        st.write(emojize(":warning: Oops! Something went wrong while creating the table."))
    finally:
        conn.close()

# Function to upload data from a CSV file into a table
def upload_csv_to_table(table_name, csv_file, db):
    try:
        df = pd.read_csv(csv_file)
        df.to_sql(table_name, sqlite3.connect(db), if_exists='append', index=False)
        st.success(emojize("Data uploaded successfully! :arrow_up:"))
        st.write(emojize(":rocket: Woohoo! Data has been successfully uploaded."))
    except Exception as e:
        st.error(f"Error uploading data: {str(e)}")
        st.write(emojize(":warning: Oops! Something went wrong while uploading data."))

# Function to delete a database
def delete_database(database_name, password):
    if password == "AviralJain@12":
        try:
            print("Attempting to delete database...")
            conn.close()  # Close the database connection
            print("Password matched. Deleting database...")
            os.remove(database_name)
            st.success(emojize("Database deleted successfully! :wastebasket:"))
            st.write(emojize(":raised_hands: Hooray! Database has been successfully deleted."))
        except Exception as e:
            print("Error occurred while deleting database:", e)
            st.error(f"Error deleting database: {str(e)}")
            st.write(emojize(":x: Oops! Something went wrong while deleting the database."))
    else:
        print("Incorrect password! Access denied.")
        st.error("Incorrect password! Access denied.")
        st.write(emojize(":lock: Oops! Incorrect password. Access denied."))

# Function to delete a table
def delete_table(table_name, db, password):
    if password == "AviralJain@12":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
            st.success(emojize("Table deleted successfully! :wastebasket:"))
            st.write(emojize(":raised_hands: Hooray! Table has been successfully deleted."))
        except Exception as e:
            conn.rollback()
            st.error(f"Error deleting table: {str(e)}")
            st.write(emojize(":x: Oops! Something went wrong while deleting the table."))
        finally:
            conn.close()
    else:
        st.error("Incorrect password! Access denied.")
        st.write(emojize(":lock: Oops! Incorrect password. Access denied."))

# Function to upload a database file
def upload_database(db_file):
    try:
        with open(db_file, 'rb') as f:
            file_content = f.read()
        with open('uploaded_database.db', 'wb') as f:
            f.write(file_content)
        st.success(emojize("Database uploaded successfully! :arrow_up:"))
        st.write(emojize(":rocket: Woohoo! Database has been successfully uploaded."))
    except Exception as e:
        st.error(f"Error uploading database: {str(e)}")
        st.write(emojize(":warning: Oops! Something went wrong while uploading the database."))

# Streamlit App
# Streamlit App
st.set_page_config(page_title="Gemini App To Retrieve SQL Data", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
st.title("Gemini SQL Assistant 🌟: Simplifying Data Retrieval")

# Introduction and Description
st.markdown("""
### Welcome to Gemini SQL Assistant!

Gemini SQL Assistant is a powerful tool that simplifies data retrieval from SQLite databases. Whether you're an expert SQL user or a beginner, this app makes database operations easy and intuitive.

#### Features:

1. **Effortless Data Retrieval:** Quickly execute SQL queries to retrieve the information you need from your database.
2. **Interactive Data Exploration:** Easily explore sample data from your tables to gain insights and understand the structure of your database.
3. **Database Operations Made Easy:** Perform various database operations such as creating tables, uploading data, and inserting or deleting records with just a few clicks.
4. **Natural Language Queries:** Use natural language to ask questions, and Gemini SQL Assistant will generate the corresponding SQL query for you, saving you time and effort.
                        
#### How to Use:

1. **Create New Database:** Start fresh by creating a new SQLite database.
2. **Select Database:** Choose an existing database to work with.
3. **Database Operations:** Perform actions like creating tables, uploading data, inserting, and deleting data.
4. **Execute SQL Queries:** Ask questions in natural language, and Gemini SQL Assistant will generate the corresponding SQL query for you!

- **Visit My Portfolio:** Explore more of my projects and skills on [my portfolio](https://jain-aviral-portfolio.netlify.app/).
- **Connect on LinkedIn:** Let's connect on [LinkedIn](https://www.linkedin.com/in/aviral-jain-b31647234) for professional networking and collaboration opportunities.
            

            

Enjoy exploring your data with Gemini SQL Assistant! 🚀
""")

# Login Section
password = st.sidebar.text_input("Password:", type="password", key="login_password")

if password == "AviralJain@12":
    st.sidebar.success("Login successful! Welcome to Gemini SQL Assistant.")

    # Default content in the middle section
    st.write("Welcome to Gemini SQL Assistant! Use the sidebar on the left to interact with the app.")

    # Option to create a new database
    create_database_option = st.sidebar.checkbox("Create New Database", key="create_db")

    if create_database_option:
        database_name = st.sidebar.text_input("Enter Database Name:", key="db_name_input_create_db")

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
                table_clicked = st.sidebar.selectbox("Select Table", tables, key="table_clicked_show_sample_db")

                if table_clicked:
                    display_sample_data(table_clicked, conn)

            # Heading for asking a question
            st.sidebar.header("Ask a Question")

            # Input field and button to ask the question
            question = st.sidebar.text_input("Input: ", key="input_ask_question")
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
                    columns[col_name] = col_type
                if st.sidebar.button("Create Table", key="create_table_btn"):
                    create_table(table_name, columns, database_name)

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
                table_to_insert = st.sidebar.selectbox("Select Table to Insert Data", tables, key="select_insert_table_insert_data")
                if table_to_insert:
                    st.sidebar.subheader(f"Insert Data into Table: {table_to_insert}")
                    cursor = conn.cursor()
                    cursor.execute(f"PRAGMA table_info({table_to_insert})")
                    columns = [column[1] for column in cursor.fetchall()]
                    data_to_insert = {}
                    for column in columns:
                        data_to_insert[column] = st.sidebar.text_input(f"Enter value for {column}:", key=f"insert_data_{column}_insert_data")
                    if st.sidebar.button("Insert Data", key="insert_data_btn"):
                        data_tuple = tuple([data_to_insert[column] for column in columns])
                        insert_data_into_table(table_to_insert, data_tuple, database_name)

            # Option to delete data from a table
            delete_option = st.sidebar.checkbox("Delete Data from Table", key="delete_data")

            if delete_option:
                table_to_delete = st.sidebar.selectbox("Select Table to Delete Data", tables, key="select_delete_table_delete_data")
                if table_to_delete:
                    st.sidebar.subheader(f"Delete Data from Table: {table_to_delete}")
                    cursor = conn.cursor()
                    cursor.execute(f"PRAGMA table_info({table_to_delete})")
                    columns = [column[1] for column in cursor.fetchall()]
                    column_to_delete = columns[0]  # Assuming the first column is used for deletion
                    value_to_delete = st.sidebar.text_input(f"Enter value in {column_to_delete} to delete:", key="delete_value_delete_data")
                    password_delete_data = st.sidebar.text_input("Enter Password:", type="password", key="password_delete_data")
                    if st.sidebar.button("Delete Data", key="delete_data_btn_delete_data"):
                        delete_data_from_table(table_to_delete, column_to_delete, value_to_delete, database_name, password_delete_data)

            # Option to delete the database
            delete_database_option = st.sidebar.checkbox("Delete Database", key="delete_db")

            if delete_database_option:
                password_delete_db = st.sidebar.text_input("Enter Password:", type="password", key="password_delete_db")
                if st.sidebar.button("Delete Database", key="delete_db_btn"):
                    delete_database(database_name, password_delete_db)
                    st.experimental_rerun()
                    st.sidebar.success("Database deletion completed!")

            # Option to delete a table
            delete_table_option = st.sidebar.checkbox("Delete Table", key="delete_table")

            if delete_table_option:
                table_to_delete = st.sidebar.selectbox("Select Table to Delete", tables, key="select_delete_table_delete_table")
                if table_to_delete:
                    password_delete_table = st.sidebar.text_input("Enter Password:", type="password", key="password_delete_table")
                    if st.sidebar.button("Delete Table", key="delete_table_btn_delete_table"):
                        delete_table(table_to_delete, database_name, password_delete_table)
                        st.experimental_rerun()
                        st.sidebar.success("Table deletion completed!")

            # Option to upload a database
            upload_database_option = st.sidebar.checkbox("Upload Database", key="upload_database")

            if upload_database_option:
                uploaded_db_file = st.sidebar.file_uploader("Upload Database File (.db)", key="uploaded_db_file")
                if uploaded_db_file is not None:
                    if st.sidebar.button("Upload Database", key="upload_db_btn"):
                        upload_database(uploaded_db_file)
                        st.experimental_rerun()
                        st.sidebar.success("Database upload completed!")

            # Close database connection
            conn.close()
else:
    st.sidebar.error("Incorrect password! Access denied.")
    st.write(emojize(":lock: Oops! Incorrect password. Access denied."))
