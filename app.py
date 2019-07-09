from flask import Flask, render_template, Response, jsonify
from camera import VideoCamera
import cv2
from keras import backend as K
import keras

app = Flask(__name__)

model = None
graph = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about_us')
def about():
    return render_template('about_us.html')

@app.route('/upload_image')
def upload():
    return render_template('upload_image.html')
def load_model():
    global model
    global graph
    model = keras.models.load_model("gender_model.h5")
    graph = K.get_session().graph

load_model()

video_stream = VideoCamera(model,graph)

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