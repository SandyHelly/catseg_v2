from flask import Flask

app = Flask(__name__)
app.secret_key = 'app secret key'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 30
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
app.config["ALLOWED_IMAGE_EXTENSIONS"] = [".JPEG", ".JPG", ".PNG"]

from app import routes