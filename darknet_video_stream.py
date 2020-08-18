from flask import Flask, render_template, Response
app = Flask(__name__)
app.config["DEBUG"] = True

#inverse resize box coordinate
def resizecoordinate(detections, originalwidth, originalheight, newwidth, newheight):
    #newdetections = list(detections)
    for detection in detections:
        detection[2][0] = detection[2][0]/originalwidth*newwidth
        detection[2][1] = detection[2][1]/originalheight*newheight
        detection[2][2] = detection[2][2]/originalwidth*newwidth
        detection[2][3] = detection[2][3]/originalheight*newheight
    #return newdetections

#count yolo detected classes number
def countclass(detections):
    count_cls_jeff = {}
    for detection in detections:
        nameTag_jeff = detection[0].decode()
        if count_cls_jeff.get(nameTag_jeff) == None:
            count_cls_jeff[nameTag_jeff] = 1
        else:
            count_cls_jeff[nameTag_jeff] += 1
    text = ''
    for key, value in count_cls_jeff.items():
        text += key + ':' + str(value) + ' ' 
    return text

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def YOLO():

    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("data/hightway.mp4")
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #cap.set(3, 1280)
    #cap.set(4, 720)
    #out = cv2.VideoWriter(
    #    "output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 10.0,
    #    (darknet.network_width(netMain), darknet.network_height(netMain)))
    print("Starting the YOLO loop...")

    # Create an image we reuse for each detect
    darknet_image = darknet.make_image(darknet.network_width(netMain),
                                    darknet.network_height(netMain),3)
    while True:
        prev_time = time.time()
        ret, frame_read = cap.read()
        height, width, _ = frame_read.shape
        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
        resizecoordinate(detections, darknet.network_width(netMain), darknet.network_height(netMain), width, height)
        text = countclass(detections)
        #cv2.putText(frame, text, (10, 40), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1)
        image = cvDrawBoxes(detections, frame_read, text, height, width)        
        convert = cv2.imencode('.jpg',image)[1].tobytes()
        # _, buffer = cv2.imencode('.jpg',image)
        # convert = buffer.tostring()
        yield(b'--frame\r\n'
              b'Content-Type:image/jpeg\r\n\r\n' + convert +b'\r\n')

    cap.release()
    out.release()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(YOLO(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    #YOLO()
    app.run(host='0.0.0.0', threaded = True, port='5002')
