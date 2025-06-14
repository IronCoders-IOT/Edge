from flask import Flask


from shared.infrastructure.database import init_db

app = Flask(__name__)


first_request = True

@app.before_request
def setup():
    global first_request
    if first_request:
        first_request = False
        # Initialize the database or any other setup tasks
        init_db()

if __name__ == '__main__':
    app.run(debug=True)