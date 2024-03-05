import cv2
import mediapipe as mp
from matplotlib.pyplot import contour
import numpy as np
import imutils


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#각도 계산 함수
def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

##모션인식
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
# 모션 횟수 셀 때 변수
counter = 0 
project = 1
if counter == 2:
    projct = 2
stage_t = None
stage_f = None

## Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while True :
        while cap.isOpened():
            ret, frame = cap.read()
            
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
        
            # Make detection
            results = pose.process(image)
        
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates
                shoulder_left = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow_left = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist_left = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                hip_left = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                thumb_left = [landmarks[mp_pose.PoseLandmark.LEFT_THUMB.value].x,landmarks[mp_pose.PoseLandmark.LEFT_THUMB.value].y]
                
                shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                
                # Calculate angle
                angle_wrist_left = calculate_angle(elbow_left, wrist_left, thumb_left)
                angle_elbow_left = calculate_angle(shoulder_left, elbow_left, wrist_left)
                angle_shoulder_left = calculate_angle(hip_left, shoulder_left, elbow_left)
                angle_elbow_right = calculate_angle(shoulder_right, elbow_right, wrist_right)
                angle_shoulder_right = calculate_angle(hip_right, shoulder_right, elbow_right)
                
                # Visualize angle
                cv2.putText(image, str(angle_wrist_left), 
                            tuple(np.multiply(wrist_left, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, str(angle_elbow_left), 
                            tuple(np.multiply(elbow_left, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, str(angle_shoulder_left), 
                            tuple(np.multiply(shoulder_left, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, str(angle_shoulder_right), 
                            tuple(np.multiply(shoulder_right, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, str(angle_elbow_right), 
                            tuple(np.multiply(elbow_right, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                 #실제 사례 계산인식
                #if angle_elbow_left > 140 and angle_elbow_right > 140 :
                #    stage_f = "down"
                #if angle_elbow_left < 50 and angle_elbow_left < 50 and stage_f =='down':
                #    stage_f= "up"
                #    counter +=1
                #print(counter)

                # sos 모션인식
                if angle_elbow_left > 140 and angle_elbow_right > 140 and angle_shoulder_right < 120 and angle_shoulder_left < 120 :
                    stage_t = "down"
                if angle_elbow_left < 120 and angle_elbow_left < 120 and angle_shoulder_right > 150 and angle_shoulder_left > 150 and stage_t =='down':
                    stage_t= "up"
                    counter +=1
                    print(counter)
                            
            except:
                pass
                
            
            # Render curl counter
            # Setup status box
            cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
            
            # Rep data
            cv2.putText(image, 'REPS', (15,12), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), 
                        (10,60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            
            # Stage data
            cv2.putText(image, 'STAGE', (65,12), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            # 실제 사고사례
            #   cv2.putText(image, stage_f, 
            #              (60,60), 
            #              cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

            #테스트 시연 sos
            cv2.putText(image, stage_t, 
                        (60,60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    )               
            
            cv2.imshow('Mediapipe Feed', image)
            if cv2.waitKey(10) & 0xFF == ord('q') or counter == 2:
                break
        
            

        while cap.isOpened():

            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, scaleFactor= 1.5, minNeighbors=3, minSize=(20,20))
            
            if len(faces) :
                for  x, y, w, h in faces :
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255,255,255), 2, cv2.LINE_4)
                    cx = int(x + w/2)
                    cy = int(y +h/2)
                    human = (cx,cy)
                    cv2.putText(frame,str(human),(cx+20,cy+20),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255),3)



            lower_red = np.array([138, 120, 20])
            upper_red = np.array([180,255,255])
            lower_yellow = np.array([15,150, 20])
            upper_yellow = np.array([35,255,255])


            mask1 = cv2.inRange(hsv, lower_red, upper_red)
            mask2 = cv2.inRange(hsv, lower_yellow, upper_yellow)

            cnts1 = cv2.findContours(mask1, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts1 = imutils.grab_contours(cnts1)

            cnts2 = cv2.findContours(mask2, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts2 = imutils.grab_contours(cnts2)

            for c in cnts1:
                area1 = cv2.contourArea(c)
                if area1 >50:
                    cv2.drawContours(frame,[c],-1,(0,255,0),3)
                    M =cv2.moments(c)

                    cx = int (M["m10"]/M["m00"])
                    cy = int (M["m01"]/M["m00"])
                    front = (cx, cy)

                    cv2.circle(frame,(cx,cy),5,(255,255,255),-1)
                    cv2.putText(frame,"red",(cx-20,cy-20),cv2.FONT_HERSHEY_PLAIN,2.5,(255,255,255),3)
                    cv2.putText(frame,str(front),(cx+20,cy+20),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255),3)
                    
                
                
            for c in cnts2:
                area2 = cv2.contourArea(c)
                if area2 >50:
                    cv2.drawContours(frame,[c],-1,(0,255,0),3)
                    M =cv2.moments(c)

                    cx = int (M["m10"]/M["m00"])
                    cy = int (M["m01"]/M["m00"])
                    back = (cx,cy)

                    cv2.circle(frame,(cx,cy),5,(255,255,255),-1)
                    cv2.putText(frame,"yellow",(cx-20,cy-20),cv2.FONT_HERSHEY_PLAIN,2.5,(255,255,255),3)
                    cv2.putText(frame,str(back),(cx+20,cy+20),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255),3)
                



            # show the frame to our screen
            cv2.imshow("Frame", frame)
            
            key = cv2.waitKey(10) & 0xFF
            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()