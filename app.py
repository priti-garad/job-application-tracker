from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# CREATE DATABASE
def init_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    # ✅ ADD JOB
    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        status = request.form["status"]

        # Prevent duplicate
        cursor.execute(
            "SELECT * FROM jobs WHERE company=? AND role=?",
            (company, role)
        )
        existing = cursor.fetchone()

        if not existing:
            cursor.execute(
                "INSERT INTO jobs (company, role, status) VALUES (?, ?, ?)",
                (company, role, status)
            )
            conn.commit()

        return redirect("/")

    # ✅ SEARCH
    search = request.args.get("search", "").strip()

    if search:
        cursor.execute(
            "SELECT * FROM jobs WHERE company LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM jobs")

    jobs = cursor.fetchall()

    # ✅ DASHBOARD COUNTS (STEP 1)
    total = len(jobs)
    applied = len([j for j in jobs if j[3] == "Applied"])
    interview = len([j for j in jobs if j[3] == "Interview"])
    rejected = len([j for j in jobs if j[3] == "Rejected"])

    conn.close()

    return render_template(
        "index.html",
        jobs=jobs,
        total=total,
        applied=applied,
        interview=interview,
        rejected=rejected
    )


# ✅ DELETE FUNCTION
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM jobs WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


# ✅ RUN APP
if __name__ == "__main__":
    app.run(debug=True)