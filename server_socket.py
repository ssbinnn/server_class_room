import socket
import csv
import threading
import time

""" 앱에서 로그인 하면서 id를 받기로 함.
    로그인 버튼 누르는 순간, 서버랑 연결됨.
    그때 id를 받아둬야함.
    
    request는 id를 이미 알고 있다는 전제하에, 현재시각을 전송 """


## 서버 호스트 및 포트 설정 ##
server_host = '192.168.161.55' # 와이파이 IP 주소
server_port = 5000

## CSV 파일 경로 설정 ##
csv_file_path = 'Class.csv'

## 접속한 클라이언트 목록 ##
client_sockets = []


#######################################################
## 요청 왔을 때 전송 함수 ##
def process_request(client_socket, request, userID):
    request = request.strip('\n') # 받은 데이터에서 줄바꿈 기호 제거

    get_date, get_time = request.split(' ') # 요일, 시간 분리
    get_hh, get_mm = map(int, get_time.split(':')) # 시, 분 분리
    get_total = 60*get_hh + get_mm # 분으로 변환


    with open(csv_file_path, 'r', encoding='utf-8') as file: # csv 파일 읽기
            reader = csv.reader(file)
            next(reader)  # 헤더 건너뛰기

            for row in reader: # 행마다 확인
                if (row[0] == userID) and (row[4] == get_date):  # 교수 번호, 요일 일치

                    start_hh, start_mm = map(int, row[5].split(':')) # 시, 분 분리
                    start_total = 60*start_hh + start_mm # 분으로 변환

                    end_hh, end_mm = map(int, row[6].split(':')) # 시, 분 분리
                    end_total = 60*end_hh + end_mm # 분으로 변환

                    if(get_total >= (start_total - 10)) and (get_total <= end_total) :
                        csv_data = ','.join(row)  # 해당 행의 데이터를 쉼표로 구분해서 문자열 생성
                        csv_data_with_newline = csv_data + '\n' # 줄바꿈으로 데이터 끝임을 표기

                        client_socket.sendall(csv_data_with_newline.encode()) # 데이터 전송
                        print(">> 서버에서 보낸 데이터 : ", csv_data)
                        break

######################################################
## 주기적으로 데이터 전송하는 함수 ##
def process_send(client_socket, interval, userID, connect_time):

    get_date, get_time = connect_time.split(' ') # 요일, 시간 분리
    get_hh, get_mm = map(int, get_time.split(':')) # 시, 분 분리
    get_total = 60*get_hh + get_mm # 분으로 변환

    while True:

        with open(csv_file_path, 'r', encoding='utf-8') as file: # csv 파일 읽기
            reader = csv.reader(file)
            next(reader)  # 헤더 건너뛰기

            for row in reader: # 행마다 확인
                if (row[0] == userID) and (row[4] == get_date):  # 교수 번호, 요일 일치

                    start_hh, start_mm = map(int, row[5].split(':')) # 시, 분 분리
                    start_total = 60*start_hh + start_mm # 분으로 변환

                    end_hh, end_mm = map(int, row[6].split(':')) # 시, 분 분리
                    end_total = 60*end_hh + end_mm # 분으로 변환

                    if(get_total >= (start_total - 10)) and (get_total <= end_total) :
                        csv_data = ','.join(row)  # 해당 행의 데이터를 쉼표로 구분해서 문자열 생성
                        csv_data_with_newline = csv_data + '\n' # 줄바꿈으로 데이터 끝임을 표기

                        client_socket.sendall(csv_data_with_newline.encode()) # 데이터 전송
                        print(">> 서버에서 주기적으로 보낸 데이터 : ", csv_data)
                        break

        time.sleep(interval) # 초 단위 쉼

        
#######################################################
## 클라이언트 접속 시 수신 스레드 생성 ##
def process_receive(client_socket, addr, userID):
    print(">> {} 클라이언트 ( {} ({}) )와 연결되었습니다.".format(userID, addr[0], addr[1]))

    while True:
        # 클라이언트로부터 요청(정보) 받기
        data = client_socket.recv(1024)

        # 클라이언트가 연결을 종료한 경우
        if not data:
            print(">> {} 클라이언트 ( {} ({}) )와 연결이 종료되었습니다.".format(userID, addr[0], addr[1]))
            client_socket.close()
            break

        request = data.decode()
        print(">> {} 클라이언트 ( {} ({}) )에서 보낸 데이터 : {}".format(userID, addr[0], addr[1], request)) # 클라이언트가 보낸 데이터

        if (request): # 요청이 온 경우
            process_request(client_socket, request, userID)
    
    # 종료한 경우
    if client_socket in client_sockets:
        client_sockets.remove(client_socket) # 리스트에서 제거
        print('>> 접속 중인 클라이언트 수 : ', len(client_sockets))

    client_socket.close()


#######################################################
## 서버 시작 ##
def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print("서버가 시작되었습니다. 클라이언트 연결 대기 중...")

    while True:
        client_socket, addr = server_socket.accept() # 클라이언트와 연결
        client_sockets.append(client_socket) # 클라이언트 목록에 추가

        data = client_socket.recv(1024)
        data = (data.decode()).strip('\n') # 받은 데이터에서 줄바꿈 기호 제거
        userID, connect_time = data.split(',') # 요일, 시간 분리

        thread_receive = threading.Thread(target=process_receive, args=(client_socket, addr, userID))
        thread_receive.start()

        thread_send = threading.Thread(target=process_send, args=(client_socket, 10, userID, connect_time))
        thread_send.start()

        print('>> 접속 중인 클라이언트 수 : ', len(client_sockets))

    #server_socket.close() # 서버는 종료하지 않음


#######################################################
if __name__ == "__main__":
    # 서버 시작
    start_server(server_host, server_port)