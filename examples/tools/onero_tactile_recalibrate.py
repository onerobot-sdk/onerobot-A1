"""重标定 Onero 夹爪的选配触觉传感器零点。

运行前：
- 夹爪已通过 CAN 直接连接，CAN 速率 1 Mbit/s；
- 两个触觉感应面均无接触、无外力，夹爪完全静止；
- 重标定不需要使能夹爪电机，本示例不会运动夹爪。

判定：
- 每个传感器返回 0x01 表示成功，其他值表示失败。
"""
import time

from onero_sdk import CanBus, OneroGripper


CHANNEL = "can0"
MODEL = "A1R"  # 与实物一致："A1L" 或 "A1R"
SETTLE_SECONDS = 1.0


def print_resultants(tactile, status, title):
    print(title)
    for sensor_id, is_online in (
        (1, status.sensor_1_online),
        (2, status.sensor_2_online),
    ):
        if is_online:
            print(f"  传感器 {sensor_id}：", tactile.read_resultant(sensor_id))


bus = CanBus(CHANNEL)
gripper = OneroGripper(bus=bus, model=MODEL, with_tactile=True, owns_bus=True)
tactile = gripper.tactile
assert tactile is not None, "with_tactile=True 应创建触觉对象"

try:
    status = tactile.get_online_status()
    print("在线状态：", status)
    if not (status.sensor_1_online or status.sensor_2_online):
        raise SystemExit("两个触觉传感器都不在线，请先检查模块接线和供电")

    print_resultants(tactile, status, "标定前合力点：")

    input("确认两个感应面无接触、夹爪静止后按 Enter 执行重标定：")
    time.sleep(SETTLE_SECONDS)

    result = tactile.recalibrate()
    print("重标定结果：", result)
    print(
        f"  传感器 1：{'成功' if result.sensor_1_success else '失败'}"
        f"（0x{result.sensor_1:02X}）"
    )
    print(
        f"  传感器 2：{'成功' if result.sensor_2_success else '失败'}"
        f"（0x{result.sensor_2:02X}）"
    )

    time.sleep(SETTLE_SECONDS)
    print_resultants(tactile, status, "标定后合力点：")
finally:
    # 本示例没有使能或运动夹爪，只释放 CAN 资源。
    gripper.shutdown()
