from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session
import sqlite3, smtplib, os, requests
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText
from base64 import b64encode
from nacl import encoding, public

# ================== APP SETUP ==================

app = Flask(__name__)
app.secret_key = "acadeno-secret-key"
bcrypt = Bcrypt(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# ================== DATABASE ==================

def get_db():
    return sqlite3.connect("users.db")

# ================== GITHUB SECRET ENGINE ==================

def update_github_secret(secret_name, secret_value):
    token = os.getenv("GITHUB_TOKEN")
    repo  = os.getenv("GITHUB_REPO")

    if not token or not repo:
        print("❌ Missing GITHUB_TOKEN or GITHUB_REPO")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    key_resp = requests.get(
        f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
        headers=headers
    )

    if key_resp.status_code != 200:
        print("❌ Failed to fetch public key :", key_resp.text)
        return

    key_data = key_resp.json()

    public_key = public.PublicKey(key_data["key"].encode(), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)

    encrypted = sealed_box.encrypt(secret_value.encode())
    encrypted_value = b64encode(encrypted).decode()

    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_data["key_id"]
    }

    put_resp = requests.put(
        f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}",
        headers=headers,
        json=payload
    )

    if put_resp.status_code == 201 or put_resp.status_code == 204:
        print(f"✅ GitHub secret '{secret_name}' updated successfully.")
    else:
        print(f"❌ Failed to update '{secret_name}':", put_resp.text)

# ================== LOGIN ==================

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email") or request.form.get("username")
        password = request.form["password"]

        db = get_db()
        c = db.cursor()
        c.execute("SELECT id,password,role FROM users WHERE username=?", (email,))
        user = c.fetchone()
        db.close()

        if user and bcrypt.check_password_hash(user[1], password):
            session["uid"] = user[0]
            session["role"] = user[2]
            return redirect("/admin-home" if user[2] == "admin" else "/user")

    return render_template("login.html")

# ================== ADMIN HOME ==================

@app.route("/admin-home")
def admin_home():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("admin_home.html")

# ================== ADD USER ==================

@app.route("/add-user", methods=["POST"])
def add_user():
    if session.get("role") != "admin":
        return redirect("/")

    email = request.form["email"]
    password = request.form["password"]
    hashed = bcrypt.generate_password_hash(password).decode()

    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO users(username,password,role,email) VALUES(?,?,?,?)",
              (email, hashed, "user", email))
    db.commit()
    db.close()

    return redirect("/admin-home")

# ================== ADD / UPDATE STUDENT ==================

@app.route("/add-student", methods=["POST"])
def add_student():
    if session.get("role") not in ["admin", "user"]:
        return redirect("/")

    student_name  = request.form["student_name"]
    student_email = request.form["student_email"]

    update_github_secret("STUDENT_NAMES", student_name)
    update_github_secret("EMAIL_TO", student_email)

    return redirect("/admin-home")

# ================== USER HOME ==================

@app.route("/user")
def user():
    return render_template("user_home.html")

# ================== FORGOT PASSWORD ==================

@app.route("/forgot", methods=["GET","POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]
        token = serializer.dumps(email)
        link = f"http://127.0.0.1:5000/reset/{token}"

        msg = MIMEText(f"Click here to reset your password:\n{link}")
        msg["Subject"] = "Password Reset"
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
        server.quit()

    return render_template("forgot.html")

# ================== RESET PASSWORD ==================

@app.route("/reset/<token>", methods=["GET","POST"])
def reset(token):
    try:
        email = serializer.loads(token, max_age=3600)
    except:
        return "Link expired"

    if request.method == "POST":
        new_pass = request.form["password"]
        hashed = bcrypt.generate_password_hash(new_pass).decode()

        db = get_db()
        c = db.cursor()
        c.execute("UPDATE users SET password=? WHERE username=?", (hashed, email))
        db.commit()
        db.close()

        return redirect("/")

    return render_template("reset.html")


# ================== LOGOUT ==================

    return redirect("/user")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================== RUN ==================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

