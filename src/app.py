"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Book, Cast
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    #este metodo busca todas las intancias de la clase characters

    #query.all(conseguimos todas las instancias de este modelo)
    characters = Character.query.all()

    serialize_characters = [character.serialize() for character in characters]
   
    return jsonify({"Character": serialize_characters, "count": len(serialize_characters)}),200
     
@app.route('/characters/<int:id>', methods=['GET'])
def get_character_by_id(id):

    character = Character.query.get(id)
    return jsonify(character.serialize())

@app.route('/character', methods=['POST'])
def create_character():
    data = request.get_json()

    data_name = data.get("name", None)
    data_gender = data.get("gender", None)
    data_species = data.get("species", None)
    data_is_alive = data.get("is_alive", None)
    
    #aqui es donde sea crea el nuevo personaje
    new_character = Character(name=data_name , gender=data_gender, species=data_species, 
                              is_alive=data_is_alive)
    print(new_character)
    #se agrega el personaje a la base de datos
    try:
        db.session.add(new_character)
    # confirmamos que se tiene que guardar 
        db.session.commit()
        return jsonify({"Character" : new_character.serialize}), 201
    except Exception as error:
        db.session.rollback()
        return error , 500

#  name = db.Column(db.String(25), unique=True, nullable=False)
#     order = db.Column(db.Integer, unique=True, nullable=False)
#     realase_date = db.Column(db.Date, unique=True, nullable=False)




@app.route('/character/<int:id>', methods=['PUT'])
def update_character(id):
    
    #obtener la informacion del body
    data = request.get_json()
    #quiero desglocar lo que quiero actualizar
    name = data.get("name", None)
    gender = data.get("gender", None)
    species = data.get("species", None)
    is_alive = data.get("is_alive", None)

    #buscar el personaje que vamos a actualizar
    character_to_edit  = Character.query.get(id)
    if not character_to_edit:
        return jsonify({"error" : "character not found"}), 404
    character_to_edit.name = name
    character_to_edit.gender = gender
    character_to_edit.species = species
    character_to_edit.is_alive = is_alive
    #actualizar los campos
    try:
        db.session.commit()
        return({"character" : character_to_edit.serialize()}), 200
    except Exception as error:
        db.session.rollback()
        return error

@app.route('/character/<int:id>', methods=['DELETE'])
def delete_character(id):
    
#para el metodo delete necesitamos recibir el id
    character_to_delete = Character.query.get(id)
    if not character_to_delete:
        return jsonify({"Error" : "Character not found"}), 404
    try:
        db.session.delete(character_to_delete)
        db.session.commit()
        return jsonify("character deleted succesfully"), 200
    except Exception as error:
        db.session.rollback()
        return error

#CRUD DE LIBROS 
@app.route('/books/', methods=['GET'])
def get_book():
    
    books = Book.query.all()

    serialize_books = [book.serialize() for book in books]
   
    return jsonify({"Book": serialize_books, "count": len(serialize_books)}),200

@app.route('/book/<int:id>', methods=['GET'])
def get_book_by_id(id):
    
    current_book = Book.query.get(id)
    if not current_book:
        return jsonify({"error" : "Book not found"}), 404

    return jsonify(current_book.serialize()), 200
#CRUD DE CAST 

@app.route('/book', methods=['POST'])
def create_book():

    data = request.get_json()

    name = data.get("name", None)
    order = data.get("order", None)
    release_date  = data.get("release_date", None)

    #aqui es donde se crean los campos para crerar el libro
    try:
        new_book = Book(name=name, order=order, realase_date=release_date)
        db.session.add(new_book)
        db.session.commit()
        return jsonify(new_book.serialize()),201
    except Exception as error:
        db.session.rollback()
        return jsonify(error), 500
#CRUD DE ELENCO 

@app.route('/book/<int:id>', methods=['DELETE'])
def delete_book(id):

    book_to_delete = Book.query.get(id)
    if not book_to_delete:
        return jsonify({"Error": "Book not found"}), 404
    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return jsonify("Book Deleted Succesfully"), 200
    except Exception as error:
        db.session.rollback()
        return jsonify(error, 500)

@app.route('/book/<int:id>', methods=['PUT'])
def update_book(id):

    data = request.get_json()
    #quiero desglocar lo que quiero actualizar
    name = data.get("name", None)
    order = data.get("order", None)
    release_date = data.get("date", None)
    
    #buscar el libro que quiero actualizar
    book_to_edit = Book.query.get(id)
    if not book_to_edit:
        return jsonify({"Error" : "book not found"}), 404
    #los campos que se deberan actualizar
    #actualizar los campos
    try: 
        book_to_edit.name = name
        book_to_edit.order = order
        book_to_edit.release_date = release_date
        db.session.commit()
        return({"book" : book_to_edit.serialize()}), 200
    except Exception as error:
        db.session.rollback()
        return error

#CRUD PARA EL CAST
@app.route('/cast/<int:book_id>/<int:character_id>', methods=['POST'])
def create_cast(book_id, character_id):
    print(book_id, character_id)

    book_to_cast = Book.query.get(book_id)
    character_to_cast = Character.query.get(character_id)

    if not book_to_cast or not character_to_cast:
        return jsonify({"error" : "Book or character not found"}), 404

    cast_exist = Cast.query.filter_by(book_id = book_id, character_id = character_id).first()

    if cast_exist:
        return jsonify({"Error": " This character already exist"}), 400

    cast = Cast(book_id = book_id, character_id=character_id)

    try: 
        db.session.add(cast)
        db.session.commit()
        return jsonify({"cast memeber" : cast.serialize()}),201
    except Exception as error:
        db.session.rollback()
        return error, 500

#todos los personajes que salieron en los libros
@app.route('/cast/book/<int:id>', methods=['GET'])
def get_cast_book(id):
    
    casts = Cast.query.filter_by(book_id=id).all()

    if not casts:
        return jsonify({"Error" : "No cast member found"}), 404

    return jsonify({"cast" : [cast.serialize() for cast in casts]})

#buscar los libros en que aparece el personaje
@app.route('/cast/character/<int:id>', methods=['GET'])
def get_books_from_characters(id):

    casts = Cast.query.filter_by(character_id=id).all()
    if not casts:
        return jsonify({"Error" : "No book for this character"}), 404
    return jsonify({"books": [book.serialize() for book in casts]})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

