from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!" #세상이 반갑지 않습니다

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
