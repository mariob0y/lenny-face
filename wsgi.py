import os
from flask import Flask, render_template, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, template_folder="templates")
DOMAIN = os.environ.get("DOMAIN", "")

# DB setup
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)


@app.before_first_request
def create_populate_db():
    db.create_all()
    if not Counter.query.get(1):
        counter = Counter(count=0)
        db.session.add(counter)
        db.session.commit()


@app.route("/")
def home():
    counter = Counter.query.get(1)
    return render_template("home.html", counter=counter, domain=DOMAIN)


@app.route("/increase", methods=["POST"])
def increase_counter():
    if request.environ.get("HTTP_ORIGIN") == DOMAIN:
        counter = Counter.query.get(1)
        counter.count += 1
        db.object_session(counter).add(counter)
        db.object_session(counter).commit()
        return jsonify({"count": counter.count})
    else:
        abort(403)


if __name__ == "__main__":
    app.run(debug=True)
