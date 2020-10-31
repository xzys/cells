import Phaser from 'phaser'

class TestScene extends Phaser.Scene {
  constructor() {
    super({ key: 'TestScene' })
  }

  create() {
    // TODO emscripten signals don't seem to work
    const test = `
import signal

def long_function_call():
  print('starting running')
  i = 0
  while True:
    i += 1

def signal_handler(signum, frame):
    raise Exception("Timed out!")

signal.signal(signal.SIGALRM, signal_handler)
signal.alarm(2)
print('set alarm')
try:
    long_function_call()
except Exception as e:
    print("Timed out!")


    `
    window.pyodide.runPython(test)
  }
}

export default TestScene
