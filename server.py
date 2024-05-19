## 서버 통합 ##
import mysocket as soc
import mydirection as dir
import myhalfdirection as hdir
import threading

# 인원수 계산 #
#raspberry = 'http://192.168.161.249:8080/?action=stream'
raspberry = int(0)
room = '113'
#thread_direction = threading.Thread(target=dir.direction, args=(raspberry, room))
thread_direction = threading.Thread(target=hdir.half_direction, args=(raspberry, room))
thread_direction.start()

## 소켓 통신 서버 호스트 및 포트 설정 ##
server_host = '192.168.161.123' # 와이파이 IP 주소
server_port = 5000
soc.start_server(server_host, server_port)