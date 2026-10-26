"""从监控线程请求减速停止。"""
import threading
import time
from onero_sdk import Arm

arm = Arm("A1R", channel="can0")

def request_stop() -> None:
    time.sleep(2.0)
    arm.stop(deceleration=3.0)

try:
    arm.enable()
    worker = threading.Thread(target=request_stop, daemon=True)
    worker.start()
    arm.movej([0.0, -0.5, 0.2, -0.6, 0.0, 0.2, 0.0], duration=5.0)
    worker.join()
finally:
    # stop() 与 disable() 含义不同；此处只关闭通信。
    arm.close()
