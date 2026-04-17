import os
import re
import sqlite3
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "skillswap-dev-secret-change-me",
)

DATABASE_PATH = Path(app.root_path) / "skillswap.db"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

TUTORS = [
    {
        "name": "Karolina Novakova",
        "initials": "KN",
        "subject": "Mathematics & Statistics",
        "subject_key": "maths",
        "rating": 5.0,
        "reviews": 142,
        "description": "PhD candidate focused on making advanced maths approachable for secondary and university students.",
        "topics": ["Calculus", "Linear Algebra", "Statistics"],
        "formats": ["online"],
        "availability": "Available today",
        "languages": "Czech, English",
        "experience": 6,
        "price": 28,
        "featured": True,
        "avatar_style": "linear-gradient(135deg, #4a7c6f 0%, #3a6459 100%)",
    },
    {
        "name": "Martin Lukas",
        "initials": "ML",
        "subject": "Programming & Computer Science",
        "subject_key": "programming",
        "rating": 4.9,
        "reviews": 98,
        "description": "Senior developer teaching Python, JavaScript, React, and algorithmic thinking through practical projects.",
        "topics": ["Python", "JavaScript", "React"],
        "formats": ["online"],
        "availability": "Available tomorrow",
        "languages": "Czech, English",
        "experience": 10,
        "price": 35,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #7c6fa4 0%, #5f5480 100%)",
    },
    {
        "name": "Sophia Berger",
        "initials": "SB",
        "subject": "English & German",
        "subject_key": "languages",
        "rating": 4.9,
        "reviews": 74,
        "description": "Cambridge-certified language tutor focused on fluency, exam preparation, and academic writing confidence.",
        "topics": ["IELTS Prep", "Business English", "German"],
        "formats": ["online", "in-person"],
        "availability": "Flexible",
        "languages": "English, German, Czech",
        "experience": 8,
        "price": 22,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #e8935a 0%, #c97040 100%)",
    },
    {
        "name": "Jan Prochazka",
        "initials": "JP",
        "subject": "Physics & Engineering",
        "subject_key": "physics",
        "rating": 4.7,
        "reviews": 61,
        "description": "University lecturer helping students with mechanics, thermodynamics, and engineering mathematics.",
        "topics": ["Mechanics", "Thermodynamics", "Exam Prep"],
        "formats": ["in-person"],
        "availability": "Weekends",
        "languages": "Czech, English",
        "experience": 12,
        "price": 30,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #4a90d9 0%, #2a6aad 100%)",
    },
    {
        "name": "Anna Kovacova",
        "initials": "AK",
        "subject": "Chemistry & Biology",
        "subject_key": "chemistry",
        "rating": 4.8,
        "reviews": 53,
        "description": "Biochemistry graduate helping learners understand concepts deeply instead of memorizing disconnected facts.",
        "topics": ["Organic Chemistry", "Cell Biology", "Lab Skills"],
        "formats": ["online"],
        "availability": "Available today",
        "languages": "Slovak, Czech, English",
        "experience": 4,
        "price": 18,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #48bb78 0%, #2f9158 100%)",
    },
    {
        "name": "Tomas Cervenka",
        "initials": "TC",
        "subject": "Music Theory & Piano",
        "subject_key": "music",
        "rating": 5.0,
        "reviews": 39,
        "description": "Conservatory-trained pianist teaching classical and modern repertoire with strong theory fundamentals.",
        "topics": ["Piano", "Harmony", "Ear Training"],
        "formats": ["online", "in-person"],
        "availability": "Flexible",
        "languages": "Czech, English",
        "experience": 9,
        "price": 25,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #e06b8b 0%, #b04060 100%)",
    },
    {
        "name": "Eva Horackova",
        "initials": "EH",
        "subject": "History & Social Studies",
        "subject_key": "history",
        "rating": 4.6,
        "reviews": 28,
        "description": "Modern history tutor making essay-heavy subjects clearer through structure, argument, and source work.",
        "topics": ["European History", "Essay Writing", "Critical Thinking"],
        "formats": ["online", "in-person"],
        "availability": "Weekdays",
        "languages": "Czech, English",
        "experience": 5,
        "price": 16,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #a0856e 0%, #7a6050 100%)",
    },
    {
        "name": "Pavel Simanek",
        "initials": "PS",
        "subject": "Economics & Finance",
        "subject_key": "economics",
        "rating": 4.8,
        "reviews": 45,
        "description": "Former analyst teaching economics and finance with practical case studies and exam-focused structure.",
        "topics": ["Microeconomics", "Corporate Finance", "Data Analysis"],
        "formats": ["online"],
        "availability": "Evenings",
        "languages": "Czech, English",
        "experience": 7,
        "price": 32,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #f6ad55 0%, #c87820 100%)",
    },
    {
        "name": "Laura Fernandez",
        "initials": "LF",
        "subject": "Spanish & French",
        "subject_key": "languages",
        "rating": 4.9,
        "reviews": 67,
        "description": "Native Spanish tutor delivering conversational confidence and structured progression from beginner to advanced.",
        "topics": ["Spanish A1-C1", "French A1-B2", "Conversation"],
        "formats": ["online"],
        "availability": "Available today",
        "languages": "Spanish, French, English",
        "experience": 6,
        "price": 20,
        "featured": False,
        "avatar_style": "linear-gradient(135deg, #667eea 0%, #4757c4 100%)",
    },
]

POPULAR_SUBJECTS = [
    ("maths", "Mathematics", "📐"),
    ("physics", "Physics", "🔬"),
    ("chemistry", "Chemistry", "🧪"),
    ("programming", "Programming", "💻"),
    ("languages", "Languages", "🗣"),
    ("music", "Music", "🎵"),
    ("history", "History", "🏛"),
    ("economics", "Economics", "💰"),
]


def _slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "tutor"


def _attach_tutor_slugs(tutors):
    seen = set()

    for tutor in tutors:
        base = _slugify(tutor["name"])
        slug = base
        suffix = 2

        while slug in seen:
            slug = f"{base}-{suffix}"
            suffix += 1

        tutor["slug"] = slug
        seen.add(slug)


_attach_tutor_slugs(TUTORS)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


def get_user_by_id(user_id):
    if user_id is None:
        return None

    return get_db().execute(
        "SELECT id, full_name, email, password_hash FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()


def get_user_by_email(email):
    if not email:
        return None

    return get_db().execute(
        "SELECT id, full_name, email, password_hash FROM users WHERE email = ?",
        (email,),
    ).fetchone()


def current_user():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id)
    if user is None and user_id is not None:
        session.pop("user_id", None)

    return user


def _first_name(full_name):
    return full_name.split(" ")[0].strip() if full_name else "there"


def _is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email or ""))


def _is_valid_password(password):
    has_letter = any(char.isalpha() for char in password)
    has_number = any(char.isdigit() for char in password)
    return len(password) >= 8 and has_letter and has_number


def _get_safe_redirect_target(default_endpoint="landing"):
    target = request.form.get("next") or request.args.get("next")
    if not target:
        return url_for(default_endpoint)

    host_url = request.host_url
    target_parts = urlparse(urljoin(host_url, target))
    host_parts = urlparse(host_url)

    if target_parts.scheme in ("http", "https") and target_parts.netloc == host_parts.netloc:
        destination = target_parts.path or "/"
        if target_parts.query:
            destination = f"{destination}?{target_parts.query}"
        return destination

    return url_for(default_endpoint)


@app.before_request
def ensure_database_ready():
    if app.config.get("DB_READY"):
        return

    init_db()
    app.config["DB_READY"] = True


@app.context_processor
def inject_common_values():
    user = current_user()
    return {
        "current_year": date.today().year,
        "auth_user": user,
        "auth_first_name": _first_name(user["full_name"]) if user else None,
    }


@app.route("/login", methods=["GET", "POST"])
@app.route("/signin", methods=["GET", "POST"])
def login():
    if current_user() is not None:
        return redirect(url_for("landing"))

    form_data = {"email": ""}
    next_target = request.args.get("next", "")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_target = request.form.get("next", "")
        form_data["email"] = email

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Welcome back, {_first_name(user['full_name'])}!", "success")
            return redirect(_get_safe_redirect_target(default_endpoint="tutors"))

    return render_template(
        "auth.html",
        active_page="login",
        auth_mode="login",
        form_data=form_data,
        next_target=next_target,
    )


@app.route("/signup", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def signup():
    if current_user() is not None:
        return redirect(url_for("landing"))

    form_data = {"full_name": "", "email": ""}
    next_target = request.args.get("next", "")

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        next_target = request.form.get("next", "")

        form_data["full_name"] = full_name
        form_data["email"] = email

        errors = []
        if len(full_name) < 2:
            errors.append("Please enter your full name.")
        if not _is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if not _is_valid_password(password):
            errors.append("Password must be at least 8 characters and include letters and numbers.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not errors and get_user_by_email(email) is not None:
            errors.append("An account with this email already exists. Try logging in.")

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, generate_password_hash(password)),
            )
            db.commit()

            user = get_user_by_email(email)
            if user is None:
                flash("Account was created, but we could not start your session. Please log in.", "error")
                return redirect(url_for("login"))

            session.clear()
            session["user_id"] = user["id"]
            flash("Your account has been created successfully.", "success")
            return redirect(_get_safe_redirect_target(default_endpoint="tutors"))

    return render_template(
        "auth.html",
        active_page="signup",
        auth_mode="signup",
        form_data=form_data,
        next_target=next_target,
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))


@app.route("/")
def landing():
    return render_template(
        "index.html",
        active_page="home",
        popular_subjects=POPULAR_SUBJECTS,
    )


@app.route("/tutors")
def tutors():
    return render_template(
        "tutors.html",
        active_page="tutors",
        tutors=TUTORS,
        tutor_count=len(TUTORS),
    )


@app.route("/tutors/<slug>")
def tutor_profile(slug):
    tutor = next((item for item in TUTORS if item["slug"] == slug), None)
    if tutor is None:
        abort(404)

    similar_tutors = [item for item in TUTORS if item["slug"] != tutor["slug"]]
    similar_tutors.sort(
        key=lambda item: (
            item["subject_key"] != tutor["subject_key"],
            -item["rating"],
            -item["reviews"],
        )
    )

    return render_template(
        "tutor_profile.html",
        active_page="tutors",
        tutor=tutor,
        similar_tutors=similar_tutors[:3],
    )


if __name__ == "__main__":
    app.run(debug=True)
