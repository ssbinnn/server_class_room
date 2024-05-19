import cv2
import numpy as np
import csv
from datetime import date

def half_direction(raspberry, room) :
        # YOLO 모델 로드
    net = cv2.dnn.readNet("C:\\Users\\tnehd\\Downloads\\yolov3_training_last.weights", "C:\\Users\\tnehd\\Downloads\\yolov3_testing.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # 클래스 이름 가져오기
    with open("coco_p.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # 라즈베리파이 카메라로부터 실시간 영상 받아오기
    cap = cv2.VideoCapture(raspberry)

    first_x, first_y = None, None
    prev_x, prev_y = None, None
    center_x, center_y = None, None

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

                if confidence > 0.5: # 사람 찾았을 때
                    # 신뢰도 0.5 이상이면 감지 되었다고 간주

                    prev_x = center_x
                    prev_y = center_y
                    print("prev : ", prev_x, prev_y)

                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                    print("좌표", center_x, center_y, w, h)

                    if first_x is None and first_y is None : # 인식이 없었던 경우,, 인식 시작 순간에 x,y 기록
                        first_x, first_y = center_x, center_y
                        print("first : ", first_x, first_y)

                    # 이동 방향 계산
                    elif first_x is not None and first_y is not None : # 인식이 있는 경우

                        if (abs(center_x - prev_x) > 100 or abs(center_y - prev_y) > 160) :
                            if ((first_x >= 0 and first_x <= 280) and (center_x >= 470 and center_x <= 640)) :  # 현 위치 x와 인식 시작됐던 prev_x의 차이 // 화면 오른쪽으로 이동
                                num+=1
                                print(num, ": 오른쪽*******************************")
                                updateCSV("right", room)
                                first_x, first_y = None, None

                            elif ((first_x > 470 and first_x <= 640) and (center_x >= 0 and center_x < 280)) :  # 화면 왼쪽으로 이동
                                num+=1
                                print(num, ": ********************************왼쪽")
                                updateCSV("left", room)
                                first_x, first_y = None, None

                            else : # 다른 구역으로 넘어가지 않고.
                                print("None")
                                first_x, first_y = None, None
                            

                        else : # 인식 유지
                            if ((first_x >= 0 and first_x <= 320) and (center_x >= 340 and center_x <= 640)) :  # 현 위치 x와 인식 시작됐던 prev_x의 차이 // 화면 오른쪽으로 이동
                                num+=1
                                print(num, ": 오른쪽*******************************")
                                updateCSV("right", room)
                                first_x, first_y = None, None

                            elif ((first_x > 320 and first_x <= 640) and (center_x >= 0 and center_x < 300)) :  # 화면 왼쪽으로 이동
                                num+=1
                                print(num, ": ********************************왼쪽")
                                updateCSV("left", room)
                                first_x, first_y = None, None
                                
        """
        # 객체가 탐지되지 않은 경우 prev_x와 prev_y를 None으로 설정합니다.
        if len(boxes) == 0:
            prev_x, prev_y = None, None
        """

        # 비 최대 억제를 통해 겹치는 박스를 제거합니다. 노이즈 제거.
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # 탐지된 객체들을 화면에 표시합니다.
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i] # 감지된 개체 둘러싼 사각형 좌표
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

        # 이미지를 화면에 출력합니다.
        cv2.imshow("output", frame)

        # 'q' 키를 누르면 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



def updateCSV(direction, room) :
    with open('Class.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        #print(rows)

    weekdays = []
    classrooms = []
    for row in rows:
        weekdays.append(row['강의 요일'])
        classrooms.append(row['강의실'])

    target_weekday = date.today().strftime("%a") #요일축약형
    target_classroom = room

    matching_rows = []
    for i, (weekday, classroom) in enumerate(zip(weekdays, classrooms)):
        if weekday == target_weekday and classroom == target_classroom:
            matching_rows.append(i)

    if matching_rows:
        print(f"Rows with the target weekday ({target_weekday}) and classroom ({target_classroom}): {matching_rows}")
    else:
        print("No matching rows found.")

    column_name = '현재인원'

    for row_index in matching_rows:
        now = int(rows[row_index][column_name])
        print(f"현재인원 (행 {row_index}): {now}")
        
        if (direction == "right") :
            rows[row_index][column_name] = now +1
        elif (direction == "left") :
            rows[row_index][column_name] = now -1

        print(f"수정된 현재인원 (행 {row_index}): {rows[row_index][column_name]}")


    # 파일 다시 쓰기
    with open('Class.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        print("수정 후 인원 : ", int(rows[row_index][column_name]))