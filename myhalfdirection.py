import cv2
import numpy as np
import csv
from datetime import date

def half_direction(camera, room) :

    # YOLO 모델 로드
    #net = cv2.dnn.readNet("C:\\Users\\tnehd\\Downloads\\yolov3_training_last.weights", "C:\\Users\\tnehd\\Downloads\\yolov3_testing.cfg")
    net = cv2.dnn.readNet("D:\graduate\practice\\test_0415\yolov3_training_last.weights", "D:\graduate\practice\\test_0415\yolov3_testing.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # 클래스 이름 가져오기
    with open("coco_p.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # 카메라로부터 실시간 영상 받아오기
    cap = cv2.VideoCapture(camera)

    first_x, first_y = None, None # 객체 탐지 시작 좌표
    prev_x, prev_y = None, None # 전 프레임에서 객체 좌표
    center_x, center_y = None, None # 현 프레임에서 객체 좌표
    bound = 20 # 인원수 세기 시 경계 값

    while True:
        _, frame = cap.read() # 카메라에서 이미지 받아옴

        height, width, channels = frame.shape # 이미지 크기 (height = 320, width = 640)

        # 이미지를 YOLO 모델에 입력할 수 있는 형태로 변환
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
        """
        320,320 : 정확도 떨어짐, 속도 빠름
        416,416 : 중간
        609,609 : 정확도 높음 속도 느림
        """

        net.setInput(blob) # 변환된 이미지를 YOLO 모델에 입력
        outs = net.forward(output_layers) # 객체 감지 결과. 탐지된 개체에 대한 정보와 위치 제공

        class_ids = [] # 객체의 class
        confidences = [] # 객체의 신뢰도
        boxes = [] # 객체 box 좌표

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5: # 신뢰도 0.5 이상이면 감지 되었다고 간주

                    prev_x = center_x
                    prev_y = center_y
                    #print("prev : ", prev_x, prev_y)

                    # 객체의 좌표
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

                    #print("좌표", center_x, center_y, w, h)

                    if first_x is None and first_y is None : # 객체 인식이 없었던 경우. 인식 시작 순간의 좌표 저장
                        first_x, first_y = center_x, center_y
                        #print("first : ", first_x, first_y)

                    elif first_x is not None and first_y is not None : # 객체 인식이 있었던 경우
                        if (abs(center_x - prev_x) > (width/2-bound)/3 or abs(center_y - prev_y) > height/3) :
                            # 프레임 끊김 현상이 있었던 경우 (이동 간격이 큰 경우)
                            if ((prev_x >= (width/4 + bound) and prev_x <= (width*0.75 - bound)) and
                                 (center_x >= (width/4 + bound) and center_x <= (width*0.75 - bound))) :
                                # 허용 범위 내에서 프레임 끊김 현상이 있었던 경우
                                # 현 위치 x와 인식 시작됐던 first_x 차이로 방향 파악
                                if ((first_x >= 0 and first_x <= width/2) and (center_x >= (width/2 + bound))) :  # 화면 오른쪽으로 이동
                                    #print("right")
                                    updateCSV("right", room)
                                    first_x, first_y = None, None

                                elif ((first_x > width/2 and first_x <= width) and (center_x <= (width/2 - bound))) :  # 화면 왼쪽으로 이동
                                    #print("left")
                                    updateCSV("left", room)
                                    first_x, first_y = None, None

                            else : # 허용 범위를 벗어난 간격일 경우
                                first_x, first_y = None, None # 객체 인식 시작 좌표를 None으로 초기화
                            

                        else :

                            # 현 위치 x와 인식 시작 위치 first_x 차이
                            if ((first_x >= 0 and first_x <= width/2) and (center_x >= (width/2 + bound) and center_x <= width)) : # 화면 오른쪽으로 이동
                                #print("right")
                                updateCSV("right", room)
                                first_x, first_y = None, None

                            elif ((first_x > width/2 and first_x <= width) and (center_x >= 0 and center_x < (width/2 - bound))) :  # 화면 왼쪽으로 이동
                                #print("left")
                                updateCSV("left", room)
                                first_x, first_y = None, None


        # 비 최대 억제를 통해 겹치는 박스를 제거 (노이즈 제거)
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # 탐지된 객체들을 화면에 표시
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i] # 감지된 개체 둘러싼 사각형 좌표
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

        # 화면에 출력
        cv2.imshow("output", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): # q키 누를 시 종료
            break

    cap.release()
    cv2.destroyAllWindows()



def updateCSV(direction, room) :
    # 객체 이동 방향에 맞게 csv 파일 업데이트
    with open('Class.csv', 'r', encoding='utf-8') as file: # csv 파일 읽기
        reader = csv.DictReader(file) # csv를 dict 형태로 읽음 (열 이름 : value)
        rows = list(reader) # 읽어온 행들을 리스트로 저장

    weekdays = []
    classrooms = []
    for row in rows:
        weekdays.append(row['강의 요일'])
        classrooms.append(row['강의실'])

    target_weekday = date.today().strftime("%a") # 요일

    matching_rows = []
    # 요일, 강의실에 해당하는 행 찾기
    for i, (weekday, classroom) in enumerate(zip(weekdays, classrooms)):
        if weekday == target_weekday and classroom == room:
            matching_rows.append(i)

    if len(matching_rows) == 0: # 해당하는 행이 없는 경우
        print(f"No matching Rows with the target weekday ({target_weekday})")

    column_name = '현재인원' # 수정할 열의 이름

    for row_index in matching_rows:
        now = int(rows[row_index][column_name])
        print(f"현재인원 (행 {row_index}): {now}")
        
        if (direction == "right") : # 오른쪽인 경우 인원수 +1
            rows[row_index][column_name] = now +1
        elif (direction == "left") : # 왼쪽인 경우 인원수 -1
            rows[row_index][column_name] = now -1
        print(f"수정된 현재인원 (행 {row_index}): {rows[row_index][column_name]}")

    # 수정된 내용을 csv에 다시 작성
    with open('Class.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        #print("수정 후 인원 : ", int(rows[row_index][column_name]))