import socket
import csv

def start_server(host, port, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print("서버가 시작되었습니다. 클라이언트 연결 대기 중...")

    while True:
        client_socket, addr = server_socket.accept() # 클라이언트와 연결
        print("클라이언트가 연결되었습니다 : ", addr)

        while True:
            # 클라이언트로부터 요청(정보) 받기
            data = client_socket.recv(1024)

            # 클라이언트가 연결을 종료한 경우
            if not data:
                print("클라이언트와의 연결이 종료되었습니다.")
                client_socket.close()
                break

            request = data.decode()
            print("받은 데이터 : ", request)

            if (request): # 요청이 온 경우
                request = request.strip('\n') # 받은 데이터에서 줄바꿈 기호 제거

                with open(file_path, 'r', encoding='utf-8') as file: # csv 파일 읽기
                    reader = csv.reader(file)
                    next(reader)  # 헤더 건너뛰기

                    for row in reader: # 행마다 확인
                        if row[0] == request:  # 교수 번호가 일치하면
                            csv_data = ','.join(row)  # 해당 행의 데이터를 쉼표로 구분해서 문자열 생성
                            csv_data_with_newline = csv_data + '\n' # 줄바꿈으로 데이터 끝임을 표기

                            client_socket.sendall(csv_data_with_newline.encode()) # 데이터 전송
                            print("보낸 데이터 : ", csv_data)
                            break

    server_socket.close() # 서버는 종료하지 않음

if __name__ == "__main__":
    # 서버 호스트 및 포트 설정
    server_host = '165.229.125.159' # 학교 와이파이 IP 주소
    server_port = 5000

    # 전송할 CSV 파일 경로 설정
    csv_file_path = 'Class.csv'

    # 서버 시작
    start_server(server_host, server_port, csv_file_path)