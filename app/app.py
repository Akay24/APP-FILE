from flask import Flask

from app.api.convert import convert_bp


app = Flask(__name__)

app.register_blueprint(convert_bp)


if __name__ == "__main__":
    app.run(debug=True)