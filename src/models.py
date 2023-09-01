from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Character(db.Model):
    __tablename__ = 'character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(50), unique=False, nullable=False)
    species = db.Column(db.String(40), unique=False, nullable=False)
    is_alive = db.Column(db.Boolean(), unique=False, nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey("house.id"), nullable=True)

    #relationships

    caste = db.relationship("Cast", backref="character", lazy=True)

    def __repr__(self):
        return f'<Character {self.name}>' 

    def serialize(self):
        return { 
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "species" : self.species,
            "is_alive" : self.is_alive
            
        }

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    order = db.Column(db.Integer, unique=True, nullable=False)
    realase_date = db.Column(db.Date, unique=True, nullable=False)

    casts_members = db.relationship("Cast", backref="book", lazy=True) 

    def __repr__(self):
        return f'<Book {self.name}>' 

    def serialize(self):
        return { 
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "realase_date" : self.realase_date,
        }

class Cast(db.Model):
    __tablename__ = 'cast'
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, 
    db.ForeignKey("character.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)



    def __repr__(self):
        return f'<Cast {self.id}>' 

    def serialize(self):
        return { 
            "id": self.id,
            "character_id": self.character_id,
            "book_id": self.book_id
        }

class House(db.Model):
    __tablename__ = 'house'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    characters = db.relationship("Character" , backref="house", lazy=True)

    def __repr__(self):
        return f'<House {self.name}>'

    def serialize(self):
        return {
            "id" : self.id,
            "name" : self.name
        }