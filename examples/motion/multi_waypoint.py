"""仿真多路点运动；真机使用前必须重新评估全部目标。"""
from onero_sdk import Arm
from onero_sdk.mujoco_backend import MujocoBackend

WAYPOINTS = [
    [0.0, -0.30, 0.20, -0.60, 0.0, 0.25, 0.0],
    [0.15, -0.45, 0.10, -0.75, 0.0, 0.35, 0.0],
    [-0.15, -0.45, 0.10, -0.75, 0.0, 0.35, 0.0],
]
backend = MujocoBackend(model_name="A1R")
arm = Arm("A1R", backend=backend)
try:
    arm.enable()
    for index, target in enumerate(WAYPOINTS, start=1):
        arm.movej(target, duration=2.0)
        print(f"已到达路点 {index}")
finally:
    arm.disable()
    backend.close()
