import cv2
import numpy as np
import csv

# YOLO 모델 로드
net = cv2.dnn.readNet("test_0415\yolov3_training_last.weights", "test_0415\yolov3_testing.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# 클래스 이름 가져오기
with open("coco_p.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# 라즈베리파이 카메라로부터 실시간 영상 받아오기
#cap = cv2.VideoCapture(0)  # 라즈베리파이 카메라가 연결된 포트 번호를 입력합니다.
cap = cv2.VideoCapture('http://192.168.126.249:8080/?action=stream')

prev_x, prev_y = None, None
# 몇 번 째 알려주는건지 확인하려구,,
num = 0

while True:
    # 카메라로부터 이미지를 받아옵니다.
    _, frame = cap.read()

    # 이미지의 크기를 가져옵니다.
    height, width, channels = frame.shape

    # 이미지를 YOLO 모델에 입력할 수 있는 형태로 변환합니다.
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
    """
    320,320 : 정확도 떨어짐, 속도 빠름
    416,416 : 중간
    609,609 : 정확도 높음 속도 느림
    """

    # 변환된 이미지를 YOLO 모델에 입력합니다.
    net.setInput(blob)

    # YOLO 모델을 통해 이미지에서 객체를 탐지합니다.
    outs = net.forward(output_layers) # 감지 결과. 탐지된 개체에 대한 정보와 위치 제공

    # 탐지된 객체들의 정보를 화면에 표시합니다.
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if classes[class_id] == "person" and confidence > 0.5: # 사람 찾았을 때
                # 신뢰도 0.5 이상이면 감지 되었다고 간주

                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

                
                # 생각해보니 화면에서 사라지고 난 뒤에 prev_x, prev_y를 처리하는 부분이 없네요 !!

                if prev_x is None and prev_y is None : # 인식이 없었던 경우,, 인식 시작 순간에 x,y 기록
                    prev_x, prev_y = x, y

               # 이동 방향 계산
                elif prev_x is not None and prev_y is not None : # 인식이 있는 경우
                    if x - prev_x > 200 :  # 현 위치 x와 인식 시작됐던 prev_x의 차이 // 화면 오른쪽으로 이동
                        num+=1
                        print(num, ": 오른쪽")
                        prev_x, prev_y = x, y

                    elif x - prev_x < -200:  # 화면 왼쪽으로 이동
                        num+=1
                        print(num, ": 왼쪽")
                        prev_x, prev_y = x, y 
                        
                        """
                        # CSV 파일 열기
                        with open('Class.csv', 'r', encoding='utf-8') as file:
                            reader = csv.DictReader(file)
                            rows = list(reader)
                            print(rows)

                        # 수정할 행과 열 찾기
                        row_index = 2  # 3번째 행 (인덱스 2)
                        column_name = '현재인원'

                        # 데이터 수정
                        now = int(rows[row_index][column_name])
                        print("현재인원 : ", now)
                        rows[row_index][column_name] = now +1

                        # 파일 다시 쓰기
                        with open('Class.csv', 'w', newline='', encoding='utf-8') as file:
                            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                            writer.writeheader()
                            for row in rows:
                                writer.writerow(row)
                            print("수정 후 인원 : ", int(rows[row_index][column_name]))
                        """

    # 객체가 탐지되지 않은 경우 prev_x와 prev_y를 None으로 설정합니다.
    if len(boxes) == 0:
        prev_x, prev_y = None, None

    # 비 최대 억제를 통해 겹치는 박스를 제거합니다. 노이즈 제거.
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # 탐지된 객체들을 화면에 표시합니다.
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i] # 감지된 개체 둘러싼 사각형 좌표
            #label = str(classes[class_ids[i]]) # 감지된 물체 이름
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            #cv2.putText(frame, label, (x, y - 10), font, 1, color, 2)
            cv2.putText(frame, "", (x, y - 10), font, 1, color, 2)

    # 이미지를 화면에 출력합니다.
    cv2.imshow("output", frame)

    # 'q' 키를 누르면 종료합니다.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()