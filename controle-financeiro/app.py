from flask import Flask, render_template

# Cria a aplicação Flask
app = Flask(__name__)

# Define uma rota (URL)
@app.route("/")
def home():
    return render_template("index.html")

# Só roda se for o arquivo principal
if __name__ == "__main__":
    app.run(debug=True)