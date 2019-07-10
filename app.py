from flask import Flask, render_template, Response, jsonify, request, redirect, flash, url_for, send_from_directory
from camera import VideoCamera
from mtcnn.mtcnn import MTCNN
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
from keras.models import load_model
import time
import tensorflow as tf
import cv2
from keras import backend as K
import keras

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
output_folder = os.path.join("static", "images", "output_faces")
app.config['OUTPUT_FOLDER'] = output_folder

model = None
graph = None

app.secret_key ="secret"

def load_model():
    global model
    global graph
    model = keras.models.load_model("gender_model.h5")
    graph = K.get_session().graph

load_model()

video_stream = VideoCamera(model,graph)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about_us')
def about():
    return render_template('about_us.html')

@app.route('/upload_image', methods=['GET','POST'])
def load_image_html():
    if request.method == 'POST':
        print(request)
        # handles when a file is selected that is not in file
        if 'file' not in request.files:
            flash('No file part')
            return 'no file part'
        # if no file is selected outputs flash message   
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return 'no selected file'
        # If a file is selected then this runs code to store the file and detect faces and gender
        if file:
            try:
                # read the file
                #file = request.files['file']

                # read the filename
                filename = file.filename
                print(filename)

                # create a path to the uploads folder
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(filepath)

                # Save the file to the uploads folder
                file.save(filepath)

                flash(f'{filename} processed successfully!')

                # time.sleep(5)
                img = plt.imread(filepath, 0)
                detector = MTCNN()
                faces = detector.detect_faces(img)
                draw_faces(filepath, faces)
                # render_template('upload_image.html')
                time.sleep(5)
                full_filename = os.path.join(app.config['OUTPUT_FOLDER'], 'output_image.jpg')
                print(f"File Name of output image: {full_filename}")
                return render_template("upload_image.html", user_image = full_filename)

                # import base64
                # data_uri = base64.b64encode(open('output_image', 'rb').read()).decode('utf-8')
                # img_tag = '<img src="data:image/png;base64,{0}">'.format(data_uri)
                # print(img_tag)
                
            except Exception as e: 
                print(e)
                return 'upload error'
    return render_template('upload_image.html')

def output():
    full_filename = os.path.join(app.config['OUTPUT_FOLDER'], 'output_image.jpg')
    return render_template("upload_image.html", user_image = full_filename)

def process_img(face):
    # K.clear_session()
    # model = keras.models.load_model("gender_model.h5")
    # graph = K.get_session().graph
    image = Image.fromarray(face)
    image = image.resize((224, 224))
    #     print(image)
    face_array = np.asarray(image)
    face_array = face_array.reshape(1,224,224,3)
    #     print(face_array)
    with graph.as_default():
        gen = model.predict(face_array)
        print(f"This is my gender output {gen}" )
        if gen[0][0] == 1:
            text = "MALE"
        else:
            text = "FEMALE"
    # K.clear_session()
    return text
    

# draw each face separately
def draw_faces(filepath, result_list):
    # load the image
    data = plt.imread(filepath)
    image = cv2.imread(filepath,1)
    # plot each face as a subplot
    for i in range(len(result_list)):
        # get coordinates
        x1, y1, width, height = result_list[i]['box']
        x2, y2 = x1 + width, y1 + height
        # define subplot
        plt.subplot(1, len(result_list), i+1)
        plt.axis('off')
        # getting an image for each face
        face = data[y1:y2, x1:x2]
        # find gender for each face
        text = process_img(face)
#         print(text)
        # plt.text(0.5, 5, text, horizontalalignment='left', verticalalignment='bottom')
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(image, text, (5,25), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0),2, lineType=cv2.LINE_AA)
        # plot face
        # plt.imshow(face)
    # show the plot
    # if os.path.isfile('static/images/output_faces/output_image.jpg'):
    #     os.remove('static/images/output_faces/output_image.jpg')
    # output_path = 
    # plt.savefig('static/images/output_faces/output_image.jpg')
    cv2.imwrite('static/images/output_faces/output_image.jpg',image)
    # plot_image = plt.imread(output_path)
    # print(plot_image)
    time.sleep(5)

    return render_template('upload_image.html')
    # return output_path

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
	return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)