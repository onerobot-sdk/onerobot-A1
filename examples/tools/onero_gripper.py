"""Onero A1 真机夹爪基础控制。

运行前：
- 确认 A1L/A1R 型号与实物一致；
- 清空夹爪和机械臂工作空间；
- 确认急停可用；
- 失能前可靠支撑机械臂。
"""
import time

from onero_sdk import Arm, OneroGripper


gripper = OneroGripper()
arm = Arm(
    "A1R",
    channel="can0",
    end_effector=gripper,
    with_gripper=True,
)

try:
    arm.enable()
    arm.gripper.open()
    time.sleep(1.0)

    arm.gripper.set_position(0.5)
    time.sleep(1.0)
    print("夹爪状态：", arm.gripper.state)

    arm.gripper.grasp()
    time.sleep(1.0)
finally:
    # disable() 会撤销机械臂保持力矩，执行前必须可靠支撑机械臂。
    arm.disable()
    arm.close()
