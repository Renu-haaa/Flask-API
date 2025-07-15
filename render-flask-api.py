from flask import Flask 

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Render!"

# For deploying to render, this section should not exist.
# render uses gunicorn to run the app!
# Just comment it out # or remove it !

# if __name__ == "__main__":
#     app.run(debug=True)
