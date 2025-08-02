from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction

from utils import logger
from action.fight import fight_utils

import time


@AgentServer.custom_action("fightProcessor")
class fightProcessor(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult:

        return CustomAction.RunResult(success=True)


@AgentServer.custom_action("fightTest")
class fightTest(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult:
        current_mapInfo = fight_utils.CheckMapInfo(context)
        # crack_pos2d_x, crack_pos_2d_y = 14, 54
        # fight_utils.MoveToTarget(context, crack_pos2d_x, crack_pos_2d_y)

        return CustomAction.RunResult(success=True)


@AgentServer.custom_action("DailyDrigt_Start")
class DailyDrigt_Start(CustomAction):
    def __init__(self) -> None:
        super().__init__()
        self.crack_pos2d_x = 14
        self.crack_pos_2d_y = 54

    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult:
        # 1. 移动到目标位置
        fight_utils.MoveToTarget(context, self.crack_pos2d_x, self.crack_pos_2d_y)
        time.sleep(2)
        if context.run_recognition(
            "DailyDrigt_Event", context.tasker.controller.post_screencap().wait().get()
        ):
            # 2.1 点击事件
            context.run_task("DailyDrigt_Event")
        else:
            return CustomAction.RunResult(success=False)

        # 2.2 回城结算
        context.run_task("Map_ReturnHome")

        # 3. 点击进入
        context.run_task("DailyDrigt_GetReward")
        return CustomAction.RunResult(success=True)
