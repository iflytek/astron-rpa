"""控制流组件实现。

提供 base_meta.json 中定义的控制流能力，包括：
- Break, Continue, Return
- If, ElseIf, Else, IfEnd, ElseEnd, ElseIfEnd
- While, WhileEnd
- ForList, ForDict, ForStep, ForEnd, ForListEnd, ForDictEnd, ForStepEnd
- Try, Catch, Finally, TryEnd, CatchEnd, FinallyEnd
- Group, GroupEnd
- Process
"""

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.control import ConditionType

_ARGS2_DYNAMICS = [
    DynamicsItem(
        key="$this.args2.show",
        expression="return ['==', '!=', '>', '>=', '<', '<=', 'in', 'notin'].includes($this.condition.value)",
    )
]


class Code:
    """控制流原子能力集合。

    这些方法主要用于流程编排，大部分为标记节点，不包含实际执行逻辑。
    """

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Break():
        """退出循环（Break）。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Continue():
        """继续下次循环（Continue）。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Return():
        """退出流程（Return）。"""
        pass

    @staticmethod
    @atomicMg.atomic(
        "Code",
        noAdvanced=True,
        inputList=[
            atomicMg.param("args1"),
            atomicMg.param(
                "condition",
            ),
            atomicMg.param("args2", dynamics=_ARGS2_DYNAMICS),
        ],
    )
    def If(args1, condition: ConditionType = ConditionType.EQ, args2=None):
        """IF条件判断。"""
        pass

    @staticmethod
    @atomicMg.atomic(
        "Code",
        noAdvanced=True,
        inputList=[
            atomicMg.param("args1"),
            atomicMg.param(
                "condition",
            ),
            atomicMg.param("args2", dynamics=_ARGS2_DYNAMICS),
        ],
    )
    def ElseIf(args1, condition: ConditionType = ConditionType.EQ, args2=None):
        """ELSE IF条件判断。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Else():
        """Else条件。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def IfEnd():
        """判断结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def ElseEnd():
        """判断结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def ElseIfEnd():
        """判断结束。"""
        pass

    @staticmethod
    @atomicMg.atomic(
        "Code",
        noAdvanced=True,
        inputList=[
            atomicMg.param("args1"),
            atomicMg.param("condition"),
            atomicMg.param("args2", dynamics=_ARGS2_DYNAMICS),
        ],
    )
    def While(args1, condition: ConditionType = ConditionType.EQ, args2=None):
        """While循环。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def WhileEnd():
        """循环结束。"""
        pass

    @staticmethod
    @atomicMg.atomic(
        "Code", noAdvanced=True, outputList=[atomicMg.param("index", types="Int"), atomicMg.param("item", types="Any")]
    )
    def ForList(list_obj: list):
        """列表For循环。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def ForListEnd():
        """列表For循环结束。"""
        pass

    @staticmethod
    @atomicMg.atomic(
        "Code", noAdvanced=True, outputList=[atomicMg.param("key", types="Any"), atomicMg.param("value", types="Any")]
    )
    def ForDict(dicts: dict):
        """字典For循环。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def ForDictEnd():
        """字典For循环结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True, outputList=[atomicMg.param("index", types="Int")])
    def ForStep(start: int, end: int, step: int = 1):
        """计数For循环。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def ForStepEnd():
        """计数For循环结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def ForEnd():
        """循环结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Try():
        """捕获异常（Try）。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def TryEnd():
        """捕获结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Catch():
        """捕获异常（Catch）。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def CatchEnd():
        """捕获结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Finally():
        """捕获异常（Finally）。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def FinallyEnd():
        """捕获结束。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def Group():
        """编组开始。"""
        pass

    @staticmethod
    @atomicMg.atomic("Code", noAdvanced=True)
    def GroupEnd():
        """编组结束。"""
        pass

    # deprecated
    # @staticmethod
    # @atomicMg.atomic(
    #     "Code",
    #     inputList=[
    #         atomicMg.param(
    #             "process",
    #             formType=AtomicFormTypeMeta(
    #                 type=AtomicFormType.SELECT.value,
    #                 params={"filters": ["Process"]},
    #             ),
    #             required=True,
    #         ),
    #         atomicMg.param(
    #             "process_param",
    #             formType=AtomicFormTypeMeta(
    #                 type=AtomicFormType.PROCESSPARAM.value,
    #                 params={"linkage": "process"},
    #             ),
    #             need_parse="str",
    #             required=False,
    #         ),
    #     ],
    #     outputList=[atomicMg.param("process_res", types="Dict")],
    # )
    # def Process(process, process_param=None):
    #     """运行子流程。"""
    #     pass
