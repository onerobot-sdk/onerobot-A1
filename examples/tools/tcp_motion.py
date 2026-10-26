"""配置 TCP 后执行工具坐标系增量运动。"""
from onero_sdk import Arm

arm = Arm("A1R", channel="can0")
try:
    arm.enable()
    arm.set_tcp(position=[0.0, 0.0, 0.15])
    input("确认工具周围至少有 5 cm 余量后按 Enter：")
    arm.movel([0.0, 0.0, 0.02, 0.0, 0.0, 0.0], frame="tool", duration=2.0)
finally:
    arm.close()
