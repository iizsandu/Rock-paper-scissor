from flask import Flask, render_template, Response
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import random
import time

app = Flask(__name__)

# Initialize the camera and other necessary variables
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 400)
detector = HandDetector(maxHands=1)
timer = 0
stateResult = False
startGame = False
score = [0, 0]
player = None

# Your game logic function
def play_game():
    global timer, stateResult, startGame, score, player
    while True:
        bg = cv2.imread('static/base.jpg')  # Adjust the path to your background image

        success, img = cap.read()
        hands, img = detector.findHands(img)

        if startGame:
            if stateResult == False:
                timer = time.time() - initialtime
                cv2.putText(bg, str(int(timer)), (560, 415), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3,
                            color=(255, 0, 255), thickness=3)
                if timer > 3:
                    stateResult = True
                    timer = 0
                    rand = random.randint(1, 3)
                    if rand == 1:
                        overimg = cv2.imread('static/paper.png')  # Adjust the path to your game images
                    elif rand == 2:
                        overimg = cv2.imread('static/rock.png')   # Adjust the path to your game images
                    else:
                        overimg = cv2.imread('static/scissors.png')  # Adjust the path to your game images
                    bg[300:602, 120:452] = overimg
                    if hands:
                        hand = hands[0]
                        fingers = detector.fingersUp(hand)
                        if fingers == [1, 1, 1, 1, 1]:
                            player = 'paper'
                        elif fingers == [0, 0, 0, 0, 0]:
                            player = 'rock'
                        elif fingers == [0, 1, 1, 0, 0]:
                            player = 'scissors'

                        if (player == 'paper' and rand == 2) or (player == 'rock' and rand == 3) or (
                                player == 'scissors' and rand == 1):
                            score[1] += 1
                        elif (player == 'paper' and rand == 3) or (player == 'rock' and rand == 1) or (
                                player == 'scissors' and rand == 2):
                            score[0] += 1

                        print(player)
                        print(score[0], score[1])

        bg[246:534, 745:1097] = img

        if stateResult:
            bg[300:602, 120:452] = overimg

        cv2.putText(bg, str(score[0]), (390, 200), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2,
                    color=(255, 255, 255), thickness=4)
        cv2.putText(bg, str(score[1]), (1045, 200), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2,
                    color=(255, 255, 255), thickness=4)

        # Convert the OpenCV image to a format suitable for HTML rendering
        _, buffer = cv2.imencode('.jpg', bg)
        img_str = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_str + b'\r\n')

# Your landing page route
@app.route('/')
def home():
    return render_template('home.html')

# The route for your game
@app.route('/play')
def play():
    global startGame, initialtime, stateResult
    startGame = True
    initialtime = time.time()
    stateResult = False
    return Response(play_game(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
