import cv2
import numpy as np

# YOLO 모델 로드
net = cv2.dnn.readNet("D:\graduate\practice\\test_0415\yolov3_training_last.weights", "D:\graduate\practice\\test_0415\yolov3_testing.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# 클래스 이름 가져오기
with open("coco_p.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# 라즈베리파이 카메라로부터 실시간 영상 받아오기
#cap = cv2.VideoCapture(0)  # 라즈베리파이 카메라가 연결된 포트 번호를 입력합니다.
cap = cv2.VideoCapture('http://192.168.126.249:8080/?action=stream')

# 추적기 초기화
#tracker_type = 'KCF'
tracker = cv2.legacy.MultiTracker_create()


# 이전 프레임에서의 객체 중심점 위치 초기화
prev_center = None
initial_center = None

while True:
    # 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        break

    height, width, channels = frame.shape
    #print("h={} w={} c={}", height, width,channels)
    # 프레임에서 객체 탐지
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
    """
    320,320 : 정확도 떨어짐, 속도 빠름
    416,416 : 중간
    609,609 : 정확도 높음 속도 느림
    """

    net.setInput(blob)
    outs = net.forward(output_layers)
    
    boxes = []
    confidences = []
    class_ids = []
    # [center_x, center_y, width, height, confidence, class_id_1, class_id_2]
    """
    center_x = int(detection[0] * width)
    center_y = int(detection[1] * height)
    w = int(detection[2] * width)
    h = int(detection[3] * height)
    x = int(center_x - w / 2)
    y = int(center_y - h / 2)
    """
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                bbox = (x, y, w, h)
                print("비박스")
                
                is_new_object = True
                for i, t in enumerate(tracker.getObjects()):
                    if np.array_equal(t, bbox):
                        is_new_object = False
                        break

                if is_new_object:
                    # 새로운 객체인 경우 추적기 추가
                    tracker.add(cv2.legacy.TrackerKCF_create(), frame, bbox)
                    print("새로운 객체 추적기 추가")

                # 객체 추적
                success, bbox = tracker.update(frame)
                if success:
                    # 추적 결과 출력
                    for i, newbox in enumerate(bbox):
                        (x, y, w, h) = [int(v) for v in newbox]
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)

                        # 객체의 중심점 계산
                        #center = ((bbox[0] + bbox[2]/2), (bbox[1] + bbox[3]/2))
                    
                    
                    """
                    if prev_center is not None:
                        # 이동 방향 결정
                        direction = "오른쪽" if center[0] > prev_center[0] else "왼쪽"
                        print(direction)
                    """
                    #prev_center = center

    # 결과 프레임 표시
    cv2.imshow("Frame", frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()