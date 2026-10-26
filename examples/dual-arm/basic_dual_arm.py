"""双臂基础创建示例。目标须按实际安装校核。"""
from onero_sdk import DualArm

dual = DualArm.create(
    left_channel="can0",
    right_channel="can1",
    arm_spacing=0.30,
)
try:
    dual.enable()
    print("左臂：", dual.left.state.joints)
    print("右臂：", dual.right.state.joints)
finally:
    # 两臂均受到可靠支撑后，才调用 dual.disable()。
    dual.left.close()
    dual.right.close()
