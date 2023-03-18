from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from werkzeug.utils import secure_filename
import os
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/iticket'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'static/singer_img'
app.config['SECRET_KEY'] = "ajbfsgnhnegrb"
db = SQLAlchemy(app)


class Singer(db.Model):
    __tablename__ = 'singer'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    number = Column(String)
    genre = Column(String)
    user_name = Column(String)
    img_url = Column(String)
    cancer = db.relationship("Cancer", backref="singer", order_by="Cancer.id")


class Place(db.Model):
    __tablename__ = 'place'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    human_capacity = Column(Integer)
    img_url = Column(String)
    cancer = db.relationship("Cancer", backref="place", order_by="Cancer.id")


class Cancer(db.Model):
    __tablename__ = 'cancer'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    img_url = Column(String)
    added_date = Column(DateTime)
    singer_id = Column(Integer, ForeignKey('singer.id'))
    place_id = Column(Integer, ForeignKey('place.id'))


with app.app_context():
    db.create_all()


@app.route('/')
def cancer_chart():
    cancer = Cancer.query.order_by(Cancer.id).all()
    return render_template('cancer chart.html', cancer=cancer)


@app.route('/profile_cancer/<int:cancer_id>')
def profile_cancer(cancer_id):
    cancer = Cancer.query.filter(Cancer.id == cancer_id).first()
    return render_template('profile_cancer.html', cancer=cancer)


@app.route('/cancer_change/<int:cancer_id>', methods=['POST', 'GET'])
def cancer_change(cancer_id):
    if request.method == "POST":
        name = request.form.get('name')
        price = request.form.get('price')
        singer_id = request.form.get('singer_id')
        place_id = request.form.get('place_id')
        date = request.form.get('date')
        date_converted = datetime.strptime(date, "%Y-%m-%d")
        Cancer.query.filter(Cancer.id == cancer_id).update({
            "name": name,
            "price": price,
            "singer_id": singer_id,
            "place_id": place_id,
            "added_date": date_converted,
        })
        img = request.files.get('img_url')
        if img:
            img_name = secure_filename(img.filename)
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
            url = "static/singer_img/" + img_name
            Cancer.query.filter(Cancer.id == cancer_id).update({
                "img_url": url
            })
        db.session.commit()
        return redirect(url_for('cancer_chart'))
    cancer = Cancer.query.filter(Cancer.id == cancer_id).first()
    singers = Singer.query.order_by(Singer.id).all()
    cancer_places = Place.query.order_by(Place.id).all()
    return render_template('cancer_change.html', cancer=cancer, singers=singers, cancer_places=cancer_places)


@app.route('/register_cancer', methods=["POST", "GET"])
def register_cancer():
    if request.method == "POST":
        name = request.form.get('name')
        price = request.form.get('price')
        singer_id = request.form.get('singer_id')
        place_id = request.form.get('place_id')
        img_url = request.files.get('img_url')
        date = request.form.get('date')
        date_converted = datetime.strptime(date, "%Y-%m-%d")
        new_date = Cancer.query.filter(Cancer.added_date == date_converted, Cancer.place_id == place_id,
                                       Cancer.singer_id == singer_id).first()
        if new_date:
            singers = Singer.query.order_by(Singer.id).all()
            cancer_places = Place.query.order_by(Place.id).all()
            return render_template('register_cancer.html', singers=singers, cancer_places=cancer_places,
                                   error="Bu vaqtda kansert bor")
        else:
            if img_url:
                img_name = secure_filename(img_url.filename)
                img_url.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
                url = "static/singer_img/" + img_name
                add = Cancer(name=name, added_date=date_converted, price=price, img_url=url, singer_id=singer_id,
                             place_id=place_id)
                db.session.add(add)
                db.session.commit()
            return redirect(url_for('cancer_chart'))
    singers = Singer.query.order_by(Singer.id).all()
    cancer_places = Place.query.order_by(Place.id).all()
    return render_template('register_cancer.html', singers=singers, cancer_places=cancer_places)


@app.route('/delete_cancer/<int:cancer_id>')
def delete_cancer(cancer_id):
    Cancer.query.filter(Cancer.id == cancer_id).delete()
    db.session.commit()
    return redirect(url_for('cancer_chart'))


@app.route('/singer_chart')
def singer_chart():
    singer = Singer.query.order_by(Singer.id).all()
    return render_template('singer_chart.html', singer=singer)


@app.route('/profile_singer/<int:singers_id>')
def profile_singer(singers_id):
    singer = Singer.query.filter(Singer.id == singers_id).first()
    return render_template('profile_singer.html', singer=singer)


@app.route('/register_singer', methods=["POST", "GET"])
def register_singer():
    if request.method == "POST":
        name_singer = request.form.get('name_singer')
        number_singer = request.form.get('number_singer')
        surname_singer = request.form.get('surname_singer')
        genre_singer = request.form.get('genre_singer')
        user_name_singer = request.form.get('user_name_singer')
        img_singer = request.files.get('img_singer')
        if img_singer:
            img_name = secure_filename(img_singer.filename)
            img_singer.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
            url = "static/singer_img/" + img_name
            add = Singer(name=name_singer, number=number_singer, surname=surname_singer, genre=genre_singer,
                         user_name=user_name_singer, img_url=url)
            db.session.add(add)
            db.session.commit()
        return redirect(url_for('singer_chart'))
    return render_template('register_singer.html')


@app.route('/singer_change/<int:singer_id>', methods=['POST', 'GET'])
def singer_change(singer_id):
    if request.method == "POST":
        name_singer = request.form.get('name_singer')
        number_singer = request.form.get('number_singer')
        surname_singer = request.form.get('surname_singer')
        genre_singer = request.form.get('genre_singer')
        user_name_singer = request.form.get('user_name_singer')
        Singer.query.filter(Singer.id == singer_id).update({
            "name": name_singer,
            "surname": surname_singer,
            "number": number_singer,
            "genre": genre_singer,
            "user_name": user_name_singer
        })
        img = request.files.get('img')
        print(img)
        if img:
            img_name = secure_filename(img.filename)
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
            url = "static/singer_img/" + img_name
            Singer.query.filter(Singer.id == singer_id).update({
                "img_url": url
            })
        db.session.commit()
        return redirect(url_for('singer_chart'))
    singer = Singer.query.filter(Singer.id == singer_id).first()
    return render_template('singer_change.html', singer=singer)


@app.route('/delete_singer/<int:singer_id>')
def delete_singer(singer_id):
    Singer.query.filter(Singer.id == singer_id).delete()
    db.session.commit()
    return redirect(url_for('singer_chart'))


@app.route('/cancer_place_chart')
def cancer_place_chart():
    cancer_place = Place.query.order_by(Place.id).all()
    return render_template('cancer_place_chart.html', cancer_place=cancer_place)


@app.route('/profile_cancer_place/<int:cancer_place_id>')
def profile_cancer_place(cancer_place_id):
    cancer_place = Place.query.filter(Place.id == cancer_place_id).first()
    return render_template('profile_cancer_place.html', cancer_place=cancer_place)


@app.route('/cancer_place_change/<int:cancer_place_id>', methods=['POST', 'GET'])
def cancer_place_change(cancer_place_id):
    if request.method == "POST":
        name = request.form.get('name')
        human_capacity = int(request.form.get('human_capacity'))
        Place.query.filter(Place.id == cancer_place_id).update({
            "name": name,
            "human_capacity": human_capacity
        })
        img = request.files.get('img')
        print(img)
        if img:
            img_name = secure_filename(img.filename)
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
            url = "static/singer_img/" + img_name
            Place.query.filter(Place.id == cancer_place_id).update({
                "img_url": url
            })
        db.session.commit()
        return redirect(url_for('cancer_place_chart'))
    cancer_place = Place.query.filter(Place.id == cancer_place_id).first()
    return render_template('cancer_place_change.html', cancer_place=cancer_place)


@app.route('/register_cancer_place', methods=["POST", "GET"])
def register_cancer_place():
    if request.method == "POST":
        name = request.form.get('name')
        human_capacity = request.form.get('human_capacity')
        img_url = request.files.get('img_url')
        if img_url:
            img_name = secure_filename(img_url.filename)
            img_url.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
            url = "static/singer_img/" + img_name
            add = Place(name=name, human_capacity=human_capacity, img_url=url)
            db.session.add(add)
            db.session.commit()
        return redirect(url_for('cancer_place_chart'))
    return render_template('register_cancer_place.html')


@app.route('/delete_cancer_place/<int:cancer_place_id>')
def delete_cancer_place(cancer_place_id):
    Place.query.filter(Place.id == cancer_place_id).delete()
    db.session.commit()
    return redirect(url_for('cancer_place_chart'))


@app.route('/menu')
def menu():
    return render_template('menu.html')


if __name__ == '__main__':
    app.run()
