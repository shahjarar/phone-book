import streamlit as st
import sqlite3
import re

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("contacts.db", check_same_thread=False)
    return conn

# Create table if not exists (with UNIQUE constraint on name)
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        phone TEXT,
        email TEXT
    )
""")
conn.commit()
conn.close()

# Validation functions
def is_valid_phone(phone):
    return re.match(r'^\d+$', phone) is not None

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

# Streamlit UI
st.title("📞 Contact Book App")

tab1, tab2, tab3, tab4 = st.tabs(["Add Contact", "View Contacts", "Update Contact", "Delete Contact"])

# 🔹 ADD CONTACT
with tab1:
    st.header("➕ Add New Contact")
    name = st.text_input("Enter Name")
    phone = st.text_input("Enter Phone Number")
    email = st.text_input("Enter Email Address")

    if st.button("Save Contact"):
        if not name or not phone or not email:
            st.warning("⚠️ All fields are required!")
        elif not is_valid_phone(phone) or not is_valid_email(email):
            st.warning("⚠️ Please enter valid details!")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
                conn.commit()
                st.success(f"✅ Contact '{name}' added successfully!")
                st.rerun()  # UI updates instantly
            except sqlite3.IntegrityError:
                st.warning(f"⚠️ Contact with name '{name}' already exists!")  # Prevent duplicate names
            finally:
                conn.close()

# 🔹 VIEW CONTACTS
with tab2:
    st.header("📋 Contact List")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone, email FROM contacts ORDER BY name ASC")
    contacts = cursor.fetchall()
    conn.close()

    if contacts:
        for contact in contacts:
            st.write(f"**👤 {contact[0]}** | 📞 {contact[1]} | ✉️ {contact[2]}")
    else:
        st.info("No contacts found!")

# 🔹 UPDATE CONTACT
with tab3:
    st.header("✏️ Update Contact")
    old_name = st.text_input("Enter Existing Contact Name")
    new_phone = st.text_input("Enter New Phone Number")
    new_email = st.text_input("Enter New Email Address")

    if st.button("Update Contact"):
        if not old_name or not new_phone or not new_email:
            st.warning("⚠️ All fields are required!")
        elif not is_valid_phone(new_phone) or not is_valid_email(new_email):
            st.warning("⚠️ Please provide valid details!")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE name=?", (old_name,))
            if cursor.fetchone():
                cursor.execute("UPDATE contacts SET phone=?, email=? WHERE name=?", (new_phone, new_email, old_name))
                conn.commit()
                st.success(f"✅ Contact '{old_name}' updated successfully!")
                st.rerun()  # UI updates instantly
            else:
                st.warning(f"⚠️ Contact '{old_name}' not found!")
            conn.close()

# 🔹 DELETE CONTACT
with tab4:
    st.header("🗑️ Delete Contact")
    delete_name = st.text_input("Enter Contact Name to Delete")

    if st.button("Delete Contact"):
        if not delete_name:
            st.warning("⚠️ Please enter a name!")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE name=?", (delete_name,))
            if cursor.fetchone():
                cursor.execute("DELETE FROM contacts WHERE name=?", (delete_name,))
                conn.commit()
                st.success(f"✅ Contact '{delete_name}' deleted successfully!")
                st.rerun()  # UI updates instantly
            else:
                st.warning(f"⚠️ Contact '{delete_name}' not found!")
            conn.close()