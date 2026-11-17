"""仅通过 CAN 直接控制 Onero 夹爪，不创建 Arm。

运行前：
- USB-CAN 适配器只连接夹爪，CAN 速率 1 Mbit/s；
- 夹爪型号与实际一致（A1L 或 A1R）；
- 夹持区域内无人和异物，供电可随时切断。
"""
import time

from onero_sdk import CanBus, OneroGripper


CHANNEL = "can0"
MODEL = "A1R"  # 与实物一致："A1L" 或 "A1R"

CYCLE_COUNT = 3
MOVE_SECONDS = 1.5
STEP_INTERVAL = 0.02
HOLD_SECONDS = 0.3
SETTLE_TOLERANCE = 0.01
SETTLE_TIMEOUT = 1.0
STALL_WINDOW = 0.25
STALL_EPS = 0.002

observed = []


def move_smoothly(gripper, name, target):
    """以固定频率分步下发目标，让动作连续，而不是一跳一停。"""
    start = gripper.refresh().position
    steps = max(1, int(MOVE_SECONDS / STEP_INTERVAL))
    print(f"→ {name}：{start:.3f} → {target:.2f}，用时约 {MOVE_SECONDS:.1f} s")

    cycle_start = time.monotonic()
    for index in range(1, steps + 1):
        if index == steps:
            position = target
        else:
            position = start + (target - start) * index / steps
        # 浮点插值在端点可能得到 1.0000000000000002 这类值，SDK 会拒绝。
        gripper.set_position(min(1.0, max(0.0, position)))
        remaining = cycle_start + index * STEP_INTERVAL - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)

    state = gripper.refresh()
    observed.append(state.position)
    last_position = state.position
    last_change = time.monotonic()
    deadline = time.monotonic() + SETTLE_TIMEOUT

    # 全闭时反馈可能停在机械端点（例如约 0.06），不会精确等于 0.0。
    # 因此位置连续一段时间不再变化时，也视为已经到达端点。
    while time.monotonic() < deadline:
        state = gripper.refresh()
        observed.append(state.position)
        if abs(state.position - target) <= SETTLE_TOLERANCE:
            print(f"   已到位：position={state.position:.3f}")
            break
        if abs(state.position - last_position) > STALL_EPS:
            last_position = state.position
            last_change = time.monotonic()
        elif time.monotonic() - last_change >= STALL_WINDOW:
            print(
                f"   已到机械端点：position={state.position:.3f}，"
                f"与目标差 {abs(state.position - target):.3f}"
            )
            break
        time.sleep(STEP_INTERVAL)

    time.sleep(HOLD_SECONDS)
    return state


bus = CanBus(CHANNEL)
gripper = OneroGripper(bus=bus, model=MODEL, owns_bus=True)

try:
    # refresh() 只查询反馈，不使能电机，也不改变当前目标。
    print("未使能反馈：", gripper.refresh())

    gripper.enable()
    print("使能后状态：", gripper.state)

    input("确认夹爪夹持区域内无人和异物后按 Enter：")
    for cycle in range(1, CYCLE_COUNT + 1):
        print(f"第 {cycle}/{CYCLE_COUNT} 次开合")
        move_smoothly(gripper, "全开", 1.0)
        move_smoothly(gripper, "全闭", 0.0)

    move_smoothly(gripper, "全开", 1.0)
    print(f"反馈开度范围：{min(observed):.3f} .. {max(observed):.3f}")
finally:
    # 失能会撤销夹持力；确认不会夹伤人员或掉落工件后再执行。
    try:
        gripper.disable()
    finally:
        # owns_bus=True 时由夹爪关闭 CAN 接口。
        gripper.shutdown()
