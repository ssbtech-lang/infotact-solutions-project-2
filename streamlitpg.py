import streamlit as st
import mysql.connector
import random
import string
import hashlib

# MySQL database connection settings
username = 'root'
password = 'Davps@2011'
host = 'localhost'
port = 3307
database = 'passwordandtext'

try:
    # Establish a connection to the MySQL database
    cnx = mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        port=port,
        database=database,
        auth_plugin='mysql_native_password'
    )

    # Create a cursor object to execute SQL queries
    cursor = cnx.cursor()

    # Initialize session state
    if 'users' not in st.session_state:
        st.session_state.users = {}
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'passwords' not in st.session_state:
        st.session_state.passwords = {}
    if 'text' not in st.session_state:
        st.session_state.text = {}

    # Function to generate password
    def generate_password(length, password_type):
        if password_type == "alphanumeric":
            characters = string.ascii_letters + string.digits + string.punctuation
        elif password_type == "numeric":
            characters = string.digits
        elif password_type == "alphabetic":
            characters = string.ascii_letters
        password = ''.join(random.choice(characters) for _ in range(length))
        return password

    # Function to create account
    def create_account(username):
        query = "INSERT INTO users (username) VALUES (%s)"
        cursor.execute(query, (username,))
        cnx.commit()
        st.session_state.users[username] = {"passwords": []}
        return True

    # Function to login
    def login(username):
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if user:
            st.session_state.current_user = username
            return True
        else:
            return False

    # Function to save passwords
    def save_passwords(username, passwords):
        query = "UPDATE users SET passwords = %s WHERE username = %s"
        passwords_str = ",".join(st.session_state.users[username]["passwords"])
        cursor.execute(query, (passwords_str.encode(), username))
        cnx.commit()

    # Function to save text
    def save_text(username, text):
        query = "UPDATE users SET text = %s WHERE username = %s"
        cursor.execute(query, (st.session_state.text[username].encode(), username))
        cnx.commit()

    # Main app
    def main():
        pages = {
            "Login/Signup": login_signup_page,
            "Password Generator": password_generator_page,
            "Text Editor": text_editor_page
        }

        if 'page' not in st.session_state:
            st.session_state.page = "Login/Signup"

        pages[st.session_state.page]()

    def login_signup_page():
        st.title("Login/Signup")
        option = st.selectbox("Select an option", ["Login", "Signup"])
        if option == "Login":
            username = st.text_input("Username")
            if st.button("Login"):
                if login(username):
                    st.session_state.page = "Password Generator"
                else:
                    st.error("Invalid username")
        elif option == "Signup":
            username = st.text_input("Username")
            if st.button("Signup"):
                if create_account(username):
                    st.session_state.page = "Password Generator"
                else:
                    st.error("Username already exists")

    def password_generator_page():
        st.title("Password Generator")
        length = st.slider("Password Length", min_value=8, max_value=128)
        password_type = st.selectbox("Password Type", ["alphanumeric", "numeric", "alphabetic"])
        if st.button("Generate Password"):
            password = generate_password(length, password_type)
            st.write("Generated Password:", password)
            if st.session_state.current_user:
                st.session_state.users[st.session_state.current_user]["passwords"].append(password)
                save_passwords(st.session_state.current_user, st.session_state.users[st.session_state.current_user]["passwords"])
        if st.button("Go to Text Editor"):
            st.session_state.page = "Text Editor"

    def text_editor_page():
        st.title("Text Editor")
        text = st.text_area("Text Editor", height=200)
        if st.button("Save"):
            if st.session_state.current_user:
                st.session_state.text[st.session_state.current_user] = text
                save_text(st.session_state.current_user, text)
            st.success("Text saved successfully")

        # Add font styling options
        font_size = st.selectbox("Font Size", [8, 10, 12, 14, 16])
        font_styles = st.multiselect("Font Style", ["Bold", "Italic", "Underline", "Strike Through"])

        # Apply font styling
        styled_text = text
        for style in font_styles:
            if style == "Bold":
                styled_text = f"<b>{styled_text}</b>"
            elif style == "Italic":
                styled_text = f"<i>{styled_text}</i>"
            elif style == "Underline":
                styled_text = f"<u>{styled_text}</u>"
            elif style == "Strike Through":
                styled_text = f"<s>{styled_text}</s>"

        # Add text alignment options
        text_align = st.selectbox("Text Align", ["Left", "Center", "Right"])
        if text_align == "Center":
            styled_text = f"<center>{styled_text}</center>"
        elif text_align == "Right":
            styled_text = f"<right>{styled_text}</right>"

        # Display styled text
        st.write(styled_text, unsafe_allow_html=True)

    if __name__ == "__main__":
        main()

except mysql.connector.Error as err:
    print(f"Error: {err}")
    st.error(f"Error: {err}")

finally:
    # Close the cursor and connection
    if 'cursor' in locals():
        cursor.close()
    if 'cnx' in locals():
        cnx.close()
