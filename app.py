from flask import Flask, render_template, request, redirect
import mysql.connector
import webbrowser as web
import time
import pyautogui as pg

app = Flask(__name__)

# Database configuration
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="emergency_contacts"
)

# Check if the "contacts" table exists; if not, create it
cursor = mydb.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contacts (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), phone VARCHAR(255))")

# Home page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get the form data
        name = request.form["name"]
        phone = request.form["phone"]
        contact_id = request.form.get("contact_id")

        if contact_id: # update existing contact
            cursor = mydb.cursor()
            cursor.execute("UPDATE contacts SET name=%s, phone=%s WHERE id=%s", (name, phone, contact_id))
        else: # insert new contact
            cursor = mydb.cursor()
            cursor.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
        mydb.commit()

    # Fetch all emergency contacts from the database
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()

    return render_template("index.html", contacts=contacts)

# Send WhatsApp message function
def send_whatsapp_message(phone_no, message):
    web.open_new_tab(f"https://web.whatsapp.com/send?phone={phone_no}&text={message}")
    time.sleep(10)
    pg.press("enter")
    time.sleep(3)
    pg.hotkey("ctrl", "w")

# Send emergency message
@app.route("/emergency", methods=["POST"])
def emergency():
    # Fetch all emergency contacts from the database
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()

    # Send WhatsApp message to each contact
    for contact in contacts:
        phone_no = contact[2] # phone number is stored in the 3rd column of the table
        message = "EMERGENCY: Please call me immediately!" # customize the message as needed
        send_whatsapp_message(phone_no, message)

    # Redirect back to the home page
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
