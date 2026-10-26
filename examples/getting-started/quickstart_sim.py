"""MuJoCo 仿真基础运动。需要安装 onero-sdk[sim]。"""
from onero_sdk import Arm
from onero_sdk.mujoco_backend import MujocoBackend

backend = MujocoBackend(model_name="A1R")
arm = Arm("A1R", backend=backend)
try:
    arm.enable()
    arm.movej([0.0, -0.5, 0.3, -1.0, 0.0, 0.5, 0.0], duration=2.0)
    print("当前关节角：", [round(value, 3) for value in arm.state.joints])
    arm.home(duration=2.0)
finally:
    arm.disable()
    backend.close()
