"""读取 Onero 夹爪选配触觉传感器。

运行前：
- Onero 夹爪已通过 USB-CAN 适配器直接连接，CAN 速率 1 Mbit/s；
- 夹爪已装配触觉模块，型号与实际一致（A1L 或 A1R）；
- 执行重标定时，触觉面不得接触任何物体。

触觉功能不要求夹爪电机使能，本示例不会使能或运动夹爪。
"""
import time

from onero_sdk import CanBus, OneroGripper


CHANNEL = "can0"
MODEL = "A1R"  # 与实物一致："A1L" 或 "A1R"
RECALIBRATE = False  # 首次安装或更换传感器后改为 True
WATCH_SECONDS = 10.0


bus = CanBus(CHANNEL)
gripper = OneroGripper(bus=bus, model=MODEL, with_tactile=True, owns_bus=True)
tactile = gripper.tactile
assert tactile is not None, "with_tactile=True 应创建触觉对象"

try:
    status = tactile.get_online_status()
    print("在线状态：", status)

    if RECALIBRATE:
        print("正在重标定，触觉面必须保持无接触……")
        result = tactile.recalibrate()
        print("重标定结果：", result)

    online = {1: status.sensor_1_online, 2: status.sensor_2_online}
    for sensor_id, is_online in online.items():
        if not is_online:
            print(f"传感器 {sensor_id} 未在线，跳过")
            continue

        point = tactile.read_resultant(sensor_id=sensor_id)
        print(f"传感器 {sensor_id} 合力点：", point)

        sample = tactile.read_points(sensor_id=sensor_id, start=0, count=10)
        for item in sample.points:
            print(
                f"  点 {item.point_id}: "
                f"Fx_raw={item.fx_raw:+4d} Fy_raw={item.fy_raw:+4d} "
                f"Fz_raw={item.fz_raw:+4d} Fz={item.fz:.1f} N"
            )

    watch_id = next((sid for sid, is_online in online.items() if is_online), None)
    if watch_id is None:
        print("两个触觉传感器都不在线，请检查模块接线和供电")
    else:
        print(f"持续读取传感器 {watch_id} 的合力点 {WATCH_SECONDS:.0f} 秒，"
              f"可用手指轻触感应面观察变化：")
        deadline = time.monotonic() + WATCH_SECONDS
        while time.monotonic() < deadline:
            point = tactile.read_resultant(sensor_id=watch_id)
            print(
                f"Fx_raw={point.fx_raw:+4d} Fy_raw={point.fy_raw:+4d} "
                f"Fz_raw={point.fz_raw:+4d} Fz={point.fz:.1f} N"
            )
            time.sleep(0.2)
finally:
    # 本示例没有使能或运动夹爪，只释放 CAN 资源。
    gripper.shutdown()
