from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

from extensions import db, login_manager
from models import User, Recipe, Ingredient

app = Flask(__name__)

app.config['SECRET_KEY'] = 'change'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
login_manager.init_app(app)

@app.route('/')
def index():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'danger')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Регистрация пройдена', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Добро пожаловать, {user.username}', 'success')
            return redirect(url_for('index'))
        flash('Неверное имя или пароль', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы','info')
    return redirect(url_for('index'))

@app.route('/recipe/create', methods=['GET', 'POST'])
@login_required
def recipe_create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        steps = request.form.get('steps', '').strip()
        ingredients = request.form.get('ingredients', '').strip()

        if not title or not description or not steps:
            flash('Заполните поля', 'danger')
            return redirect(url_for('recipe_create'))

        recipe = Recipe(title=title, description=description, steps=steps, author=current_user)

        if ingredients:
            for item in ingredients.split(','):
                name = item.strip()
                if not name:
                    continue

                ing = Ingredient.query.filter_by(name=name).first()
                if not ing:
                    ing = Ingredient(name=name)
                    db.session.add(ing)

                if ing not in recipe.ingredients:
                    recipe.ingredients.append(ing)

        db.session.add(recipe)
        db.session.commit()
        flash('Рецепт добавлен', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    return render_template('recipe_create.html')

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)