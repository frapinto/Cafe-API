from flask import Flask, jsonify, render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path= find_dotenv()
load_dotenv(dotenv_path)

print(f"DEBUG - Loaded .env at: {dotenv_path}")
print(f"DEBUG - TopSecretApiKey value: {os.getenv('TopSecretApiKey')}")

API_KEY= os.getenv("TopSecretApiKey")

app = Flask(__name__)
Base = declarative_base()

# connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SECRET_KEY'] = API_KEY
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafe(db.Model):
    __tablename__ = 'cafe'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    map_url = Column(String(500), nullable=False)
    img_url = Column(String(500), nullable=False)
    location = Column(String(250), nullable=False)
    seats = Column(String(250), nullable=False)
    has_toilet = Column(Boolean, nullable=False)
    has_wifi = Column(Boolean, nullable=False)
    has_sockets = Column(Boolean, nullable=False)
    can_take_calls = Column(Boolean, nullable=False)
    coffee_price = Column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

with app.app_context():
    db.create_all()
    print(f"Total cafes in database: {Cafe.query.count()}")

@app.route("/")
def home():
    cafes = Cafe.query.all()
    return render_template("index.html", cafes=cafes)

@app.route("/details/<int:id>")
def details(id):
    cafe = db.get_or_404(Cafe, id)
    return render_template("details.html", cafe=cafe)


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":

        sockets = request.form.get("sockets") == "true"
        wifi = request.form.get("wifi") == "true"
        toilet = request.form.get("toilet") == "true"
        calls = request.form.get("calls") == "true"

        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=sockets,
            has_wifi=wifi,
            has_toilet=toilet,
            can_take_calls=calls,
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )

        db.session.add(new_cafe)
        db.session.commit()

        flash("Cafe added successfully!")
        return redirect(url_for('home'))


    return render_template("add.html")


@app.route('/delete')
def delete():
    cafe_id = request.args.get('id')

    try:
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        db.session.delete(cafe_to_delete)
        db.session.commit()
        flash('Cafe deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting cafe. Please try again.', 'error')
        app.logger.error(f"Error deleting cafe {cafe_id}: {str(e)}")
    finally:
        db.session.close()

    return redirect(url_for('home'))

@app.route("/debug")
def debug():
    cafes = Cafe.query.all()
    return jsonify([cafe.to_dict() for cafe in cafes])


if __name__ == "__main__":
    app.run(debug=True)