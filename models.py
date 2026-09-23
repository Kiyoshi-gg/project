from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager

recipe_ingredient = db.Table('recipe_ingredient', db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
                             db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
                             db.Column('quantity', db.String(50)))
favorites = db.Table('favorites', db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipes = db.relationship('Recipe', backref='author', lazy=True, cascade='all, delete-orphan')
    favorite_recipes = db.relationship('Recipe', secondary=favorites, backref=db.backref('favorited_by', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
       self.password_hash = generate_password_hash(password)
    def check_password(self, password):
       return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    def __repr__(self):
        return f'<Ingredient {self.name}>'

class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredients = db.relationship('Ingredient', secondary=recipe_ingredient, backref=db.backref('recipes', lazy='dynamic'), lazy='joined')
    def __repr__(self):
        return f'<Recipe {self.title}>'