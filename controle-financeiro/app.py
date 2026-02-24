from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-secreta"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"

# Inicializar banco de dados e gerenciador de login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Modelo do usuário
class User(UserMixin, db.Model):
    """Representa um usuário no sistema"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Transaction(db.Model):
    """Representa uma transação financeira do usuário"""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "ganho" ou "gasto"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@app.route("/add", methods=["POST"])
@login_required
def add_transaction():
    """Adiciona uma nova transação para o usuário logado"""
    description = request.form["description"]
    amount = float(request.form["amount"])
    type_ = request.form["type"]

    t = Transaction(
        description=description,
        amount=amount,
        type=type_,
        user_id=current_user.id
    )
    db.session.add(t)
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/delete/<int:id>")
@login_required
def delete_transaction(id):
    """Deleta uma transação do usuário logado"""
    t = Transaction.query.get_or_404(id)

    if t.user_id != current_user.id:
        return "Acesso negado", 403

    db.session.delete(t)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Exibe o painel de controle com as transações do usuário"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", user=current_user, transactions=transactions)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Trata login de usuários"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Trata registro de novos usuários"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    """Faz logout do usuário"""
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)