from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    """Video streaming generator function."""
    cap = cv2.VideoCapture("data/hightway.mp4")
    while True:
        ret, frame_read = cap.read()
    #img = cv2.imread("data/dog.jpg")
    #img = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 

        frame = cv2.imencode('.jpg', frame_read)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(host='0.0.0.0', threaded = True, port='5001')
