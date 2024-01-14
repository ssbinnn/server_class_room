import socket
import csv
from _thread import *

## 서버 호스트 및 포트 설정 ##
server_host = '172.30.1.96' # 와이파이 IP 주소
server_port = 5000

## CSV 파일 경로 설정 ##
csv_file_path = 'Class.csv'

## 접속한 클라이언트 목록 ##
client_sockets = []

#######################################################
## 클라이언트 접속 시 스레드 생성 ##
def threaded(client_socket, addr):
    print('>> 클라이언트와 연결되었습니다 :', addr[0], '(', addr[1], ')')

    ## process until client disconnect ##

    while True:
        # 클라이언트로부터 요청(정보) 받기
        data = client_socket.recv(1024)

        # 클라이언트가 연결을 종료한 경우
        if not data:
            print(">>", addr[0], "(", addr[1], ")와 연결이 종료되었습니다.")
            client_socket.close()
            break

        request = data.decode()
        print(">>", addr[0], "(", addr[1], ")에서 보낸 데이터 : ", request) # 클라이언트가 보낸 데이터

        if (request): # 요청이 온 경우
            request = request.strip('\n') # 받은 데이터에서 줄바꿈 기호 제거

            with open(csv_file_path, 'r', encoding='utf-8') as file: # csv 파일 읽기
                reader = csv.reader(file)
                next(reader)  # 헤더 건너뛰기

                for row in reader: # 행마다 확인
                    if row[0] == request:  # 교수 번호가 일치하면
                        csv_data = ','.join(row)  # 해당 행의 데이터를 쉼표로 구분해서 문자열 생성
                        csv_data_with_newline = csv_data + '\n' # 줄바꿈으로 데이터 끝임을 표기

                        client_socket.sendall(csv_data_with_newline.encode()) # 데이터 전송
                        print(">> 서버에서 보낸 데이터 : ", csv_data)
                        break
    
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
        start_new_thread(threaded, (client_socket, addr)) # 해당 클라이언트 스레드 실행

        print('>> 접속 중인 클라이언트 수 : ', len(client_sockets))

        
    #server_socket.close() # 서버는 종료하지 않음




#######################################################
if __name__ == "__main__":
    # 서버 시작
    start_server(server_host, server_port)