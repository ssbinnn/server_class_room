import socket

def start_server(host, port, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"서버가 시작되었습니다. 클라이언트 연결 대기 중...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"클라이언트가 연결되었습니다: {addr}")

        while True:
            # 클라이언트로부터 요청 받기
            data = client_socket.recv(1024)

            # 클라이언트가 연결을 종료한 경우
            if not data:
                print("클라이언트와의 연결이 종료되었습니다.")
                client_socket.close()
                break

            request = data.decode()
            print("받은 데이터 : ", request)

            if request == "refresh\n":
                # CSV 파일 읽기
                with open(file_path, 'r') as file:
                    csv_data = file.read()
                    print("보낸 데이터 : ", csv_data)

                # 클라이언트에게 CSV 데이터 전송
                client_socket.sendall(csv_data.encode())

    server_socket.close()

if __name__ == "__main__":
    # 서버 호스트 및 포트 설정
    server_host = '165.229.229.47' # 학교 와이파이 IP 주소
    server_port = 5000

    # 전송할 CSV 파일 경로 설정
    csv_file_path = 'D:\graduate\Class.csv'

    # 서버 시작
    start_server(server_host, server_port, csv_file_path)