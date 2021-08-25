from app import app
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
from model_inference import inference
import boto3

#set s3 keys and login
AWS_BUCKET = os.environ['AWS_BUCKET']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

#setup
s3 = boto3.resource('s3')
s3_client = boto3.client('s3', config=boto3.session.Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = basedir + '/static/image_storage/users_images'
model = inference.get_model()
name4pred = 'name4pred.jpg'


@app.errorhandler(413)
def app_handle_413(e):
    flash('IMAGE MUST BE < 1 Mb!')
    return render_template("index.html", title='Main Page'), 413

@app.errorhandler(404)
def app_handle_404(e):
    flash('This page doesnt exist!')
    return render_template("index.html", title='Main Page'), 404


#refreshing
@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            session['filename'] = secure_filename(file.filename)
            if os.path.splitext(session['filename'])[1].upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                session['file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], name4pred)
                file.save(session['file_path'])
                inference.make_prediction(model)
                return redirect(url_for('result'))
            else:
                flash('IMAGE MUST BE .JPG or .PNG')
                return render_template("index.html", title='Main Page')
    return render_template("index.html", title='Main Page')

@app.route('/gallery')
def gallery():
    bucket_items = []
    urls_list = []
    for item in s3.Bucket(AWS_BUCKET).objects.all():
        bucket_items.append(item.key)
    gallery_images = [gi for gi in bucket_items if '_mask.jpg' in gi]
    #generate presigned links to show images from private s3 bucket
    for object_name in gallery_images:
        url = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': AWS_BUCKET,
                                                        'Key': object_name},
                                                ExpiresIn=3600)
        urls_list.append(url)
    return render_template("gallery.html", title='Gallery', gallery_images=urls_list)

@app.route('/result', methods=['GET','POST'])
def result():
    if request.method == 'POST':
        if request.form['submit_button'] == 'TRY AGAIN!':
            return redirect(url_for('index'))
        elif request.form['submit_button'] == 'ADD TO GALLERY!':
            MASK_PATH = 'app/static/image_storage/seg_masks/name4pred_mask.jpg'
            response = s3_client.upload_file(MASK_PATH, AWS_BUCKET, 'images/seg_masks/'+session['filename'][:-4]+'_mask.jpg')
            return redirect(url_for('gallery'))
        else: pass
    elif request.method == 'GET':
        return render_template("result.html", title='Result', image_name=name4pred[:-4])