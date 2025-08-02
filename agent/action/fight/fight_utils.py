from maa.context import Context
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time


@dataclass
class MapInfo:
    map_name: str
    x: Optional[int] = None
    y: Optional[int] = None
    current_weight: Optional[int] = None
    max_weight: Optional[int] = None
    food: Optional[str] = None


def CheckMapInfo(context: Context) -> Optional[MapInfo]:
    image = context.tasker.controller.post_screencap().wait().get()
    if recoDetail := context.run_recognition(
        "MapInfoCheck",
        image,
        pipeline_override={
            "MapInfoCheck": {"recognition": "OCR", "roi": [0, 0, 256, 140]}
        },
    ):
        # print(f"检查到地图信息, {recoDetail.filterd_results}")
        return parse_map_info(recoDetail.filterd_results)
    return None


def parse_map_info(ocr_results: List) -> MapInfo:
    """解析OCR结果为MapInfo结构

    Args:
        ocr_results: OCR识别结果列表

    Returns:
        MapInfo: 解析后的地图信息
    """
    map_info = MapInfo(map_name="未知地图")

    for result in ocr_results:
        text = result.text
        if "（" in text and "）" in text:
            # 处理地图名称和坐标
            map_name_part = text.split("（")[0]
            coord_part = text.split("（")[1].split("）")[0]
            map_info.map_name = map_name_part
            # 解析坐标为x和y
            if "," in coord_part:
                try:
                    x, y = coord_part.split(",")
                    map_info.x = int(x.strip())
                    map_info.y = int(y.strip())
                except ValueError:
                    # 坐标格式不正确时保持为None
                    pass
        elif "负重：" in text:
            # 处理负重信息
            weight_part = text.split("：")[1]
            if "/" in weight_part:
                try:
                    current, max_w = weight_part.split("/")
                    map_info.current_weight = int(current.strip())
                    map_info.max_weight = int(max_w.strip())
                except ValueError:
                    # 负重格式不正确时保持为None
                    pass
        elif "食物：" in text:
            # 处理食物信息
            food_part = text.split("：")[1]
            map_info.food = food_part

    print(f"解析后的地图信息: {map_info}")
    return map_info


def MoveToTarget(context: Context, target_x: int, target_y: int) -> bool:
    """从当前位置移动到目标位置

    Args:
        context: 上下文对象
        target_x: 目标位置x坐标
        target_y: 目标位置y坐标

    Returns:
        bool: 是否成功到达目标位置
    """
    # 获取当前位置
    current_map_info = CheckMapInfo(context)
    if not current_map_info or current_map_info.x is None or current_map_info.y is None:
        print("无法获取当前位置信息")
        return False

    current_x, current_y = current_map_info.x, current_map_info.y
    print(f"当前位置: ({current_x}, {current_y}), 目标位置: ({target_x}, {target_y})")

    # 简单的路径规划: 先横后竖
    # 实际应用中可能需要更复杂的路径规划算法
    steps = []

    # 横向移动
    if current_x < target_x:
        steps.extend(["moveRight"] * (target_x - current_x))
    elif current_x > target_x:
        steps.extend(["moveLeft"] * (current_x - target_x))

    # 纵向移动
    if current_y < target_y:
        steps.extend(["moveDown"] * (target_y - current_y))
    elif current_y > target_y:
        steps.extend(["moveUp"] * (current_y - target_y))

    # 执行移动
    for step in steps:
        # 检查是否有障碍物
        if CheckObstacle(context):
            print("检测到障碍物，尝试绕行...")
            # 简单的绕行逻辑: 先上移再继续
            if not context.run_action("moveUp"):
                print("绕行失败")
                return False
            time.sleep(0.5)

        # 执行移动动作
        print(f"执行动作: {step}")
        if not context.run_action(step):
            print(f"执行动作 {step} 失败")
            return False
        time.sleep(0.5)  # 等待移动完成

    # 到达目标位置后再次检查
    new_map_info = CheckMapInfo(context)
    if new_map_info and new_map_info.x == target_x and new_map_info.y == target_y:
        print(f"成功到达目标位置: ({target_x}, {target_y})")
        return True
    else:
        print(f"未到达目标位置，当前位置: ({new_map_info.x}, {new_map_info.y})")
        return False


def CheckObstacle(context: Context) -> bool:
    """检查当前位置是否有障碍物

    Args:
        context: 上下文对象

    Returns:
        bool: 是否存在障碍物
    """
    # 这里实现障碍物检测逻辑
    # 示例: 使用OCR检测特定文本或使用图像识别检测障碍物
    image = context.tasker.controller.post_screencap().wait().get()
    if obstacle_reco := context.run_recognition(
        "ObstacleCheck",
        image,
        pipeline_override={
            "ObstacleCheck": {"recognition": "OCR", "roi": [0, 0, 720, 1280]}
        },
    ):
        # 检查是否有表示障碍物的文本
        for result in obstacle_reco.filterd_results:
            if "障碍物" in result.text or "无法通过" in result.text:
                return True
    return False
