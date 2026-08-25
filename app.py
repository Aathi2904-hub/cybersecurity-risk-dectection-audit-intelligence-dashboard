from flask import Flask, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)

# Session use panna secret key
app.secret_key = "cybersecurity_dashboard_secret"


# ---------------- GET DATA ----------------

def get_data():

    with open(
        "data.csv",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        return list(csv.DictReader(file))


# ---------------- DASHBOARD DATA ----------------

def dashboard_data(data):

    total_risks = len(data)

    # High Risk
    high_risk = sum(
        1
        for row in data
        if row.get("Risk_Level", "").strip().lower() == "high"
    )

    # Medium Risk
    medium_risk = sum(
        1
        for row in data
        if row.get("Risk_Level", "").strip().lower() == "medium"
    )

    # Low Risk
    low_risk = sum(
        1
        for row in data
        if row.get("Risk_Level", "").strip().lower() == "low"
    )


    # ---------------- EVENT TYPE ANALYSIS ----------------

    event_counts = {}

    for row in data:

        event = row.get("Event_Type", "").strip()

        if event:

            event_counts[event] = (
                event_counts.get(event, 0) + 1
            )


    # ---------------- RISK SCORE ANALYSIS ----------------

    risk_scores = []

    for row in data:

        try:
            score = int(
                row.get("Risk_Score", "0").strip()
            )

        except (ValueError, AttributeError):
            score = 0

        risk_scores.append({
            "id": row.get("Risk_ID", ""),
            "score": score
        })


    # ---------------- DATE-WISE RISK ANALYSIS ----------------

    date_counts = {}

    for row in data:

        date = row.get(
            "Identified_Date",
            ""
        ).strip()

        if date:

            date_counts[date] = (
                date_counts.get(date, 0) + 1
            )


    return {

        "data": data,

        "total_risks": total_risks,

        "high_risk": high_risk,

        "medium_risk": medium_risk,

        "low_risk": low_risk,

        "event_counts": event_counts,

        "risk_scores": risk_scores,

        "date_counts": date_counts
    }


# =====================================================
# LOGIN
# =====================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()


        # Correct username and password

        if username == "admin" and password == "admin123":

            # Login session
            session["logged_in"] = True

            return redirect(
                url_for("dashboard")
            )


        # Wrong login

        return render_template(
            "login.html",
            error="Invalid username or password"
        )


    return render_template("login.html")


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    # Login check

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    # Get CSV data

    data = get_data()


    # ---------------- SEARCH ----------------

    search = request.args.get(
        "search",
        ""
    ).strip().lower()


    if search:

        data = [

            row

            for row in data

            if search in row.get(
                "Risk_ID",
                ""
            ).lower()

            or

            search in row.get(
                "Event_Type",
                ""
            ).lower()

        ]


    # Create dashboard data

    dashboard = dashboard_data(data)


    # Search value send to HTML

    dashboard["search"] = search


    return render_template(
        "dashboard.html",
        **dashboard
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    # Clear login session

    session.clear()

    return redirect(
        url_for("login")
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )