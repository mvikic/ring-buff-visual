from threading import Lock

from flask import Flask, jsonify, render_template

app = Flask(__name__)


class RingBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0
        self.tail = 0
        self.size = 0
        self.lock = Lock()

    def write(self, data):
        with self.lock:
            self.buffer[self.head] = data
            self.head = (self.head + 1) % self.capacity
            if self.size < self.capacity:
                self.size += 1
            else:
                self.tail = (self.tail + 1) % self.capacity

    def read(self):
        with self.lock:
            if self.size == 0:
                return None
            data = self.buffer[self.tail]
            self.buffer[self.tail] = None
            self.tail = (self.tail + 1) % self.capacity
            self.size -= 1
            return data

    def get_state(self):
        return {
            "buffer": self.buffer,
            "head": self.head,
            "tail": self.tail,
            "size": self.size,
            "capacity": self.capacity,
        }


buffer = RingBuffer(6)
next_value = 1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/state")
def get_state():
    return jsonify(buffer.get_state())


@app.route("/write", methods=["POST"])
def write():
    global next_value
    buffer.write(next_value)
    next_value += 1
    return jsonify(buffer.get_state())


@app.route("/read", methods=["POST"])
def read():
    buffer.read()
    return jsonify(buffer.get_state())


@app.route("/reset", methods=["POST"])
def reset():
    global next_value
    global buffer
    buffer = RingBuffer(6)
    next_value = 1
    return jsonify(buffer.get_state())


if __name__ == "__main__":
    app.run(debug=True)
