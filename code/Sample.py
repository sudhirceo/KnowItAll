import sqlite3

def create_user_table():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, active INTEGER, failed_attempts INTEGER)''')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, active, failed_attempts) VALUES (?, ?, 1, 0)", (username, password))
    conn.commit()
    conn.close()

def find_user_by_username(username):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def verify_password(user, password):
    return user[2] == password

def is_active(user):
    return user[3] == 1

def update_failed_attempts(user):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute("UPDATE users SET failed_attempts=? WHERE id=?", (user[4] + 1, user[0]))
    conn.commit()
    conn.close()

def lock_account(user):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute("UPDATE users SET active=0 WHERE id=?", (user[0],))
    conn.commit()
    conn.close()

def authenticate(username, password):
    user = find_user_by_username(username)

    if user is None:
        return 'User not found'

    if not verify_password(user, password):
        return 'Invalid password'

    if not is_active(user):
        return 'User account is inactive'

    login_attempts = 0
    while login_attempts < 3:
        otp = generate_otp()
        send_otp(user, otp)
        entered_otp = input("Enter the OTP: ")

        if entered_otp == otp:
            return 'Authenticated'
        else:
            login_attempts += 1
            update_failed_attempts(user)
            if login_attempts == 3:
                lock_account(user)
                return 'Max OTP attempts reached'

    return 'Error'