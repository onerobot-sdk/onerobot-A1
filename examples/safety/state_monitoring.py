"""以固定频率读取机械臂状态。"""
import time
from onero_sdk import Arm

arm = Arm("A1R", channel="can0")
try:
    arm.enable()
    for _ in range(50):
        state = arm.state
        print({
            "joints": [round(value, 3) for value in state.joints],
            "velocities": [round(value, 3) for value in state.velocities],
            "torques": [round(value, 3) for value in state.torques],
        })
        time.sleep(0.1)
finally:
    # 本示例只关闭通信；失能前必须确认机械臂受到可靠支撑。
    arm.close()
