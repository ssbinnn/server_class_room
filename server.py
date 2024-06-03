## 서버 통합 ##
import mysocket as soc
import mydirection as dir
import myhalfdirection as hdir
import threading

## 인원수 계산 ##
#raspberry = 'http://192.168.161.249:8080/?action=stream'
camera = int(0) # 웹캠 연결
room = '113' # 강의실
thread_direction = threading.Thread(target=hdir.half_direction, args=(camera, room)) # 인원 수 계산 스레드
thread_direction.start()

## 소켓 통신 서버 호스트 및 포트 설정 ##
server_host = '165.229.229.197' # 와이파이 IP 주소
server_port = 5000
soc.start_server(server_host, server_port)