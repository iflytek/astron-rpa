from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from astronverse.scheduler.apis.connector import executor as executor_module
from astronverse.scheduler.apis.connector.executor import RobotInfo, TaskInfo, executor_run_list
from astronverse.scheduler.core.executor.executor import ExecuteStatus, TaskExecuteStatus


def make_executor(status: ExecuteStatus, reason: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        execute_status=status,
        execute_reason=reason,
        execute_data={},
    )


def make_svc(create_side_effect) -> SimpleNamespace:
    executor_mg = MagicMock()
    executor_mg.status.return_value = False
    executor_mg.create.side_effect = create_side_effect

    return SimpleNamespace(
        executor_mg=executor_mg,
        terminal_mod=False,
        terminal_task_stop=False,
        rpa_route_port=0,
    )


def make_task(exceptional: str, retry_num: int) -> TaskInfo:
    return TaskInfo(
        trigger_id="task-1",
        trigger_name="retry regression",
        task_type="schedule",
        exceptional=exceptional,
        retry_num=retry_num,
        callback_project_ids=[
            RobotInfo(robotId="robot-1", robotName="failing robot", sort=1),
            RobotInfo(robotId="robot-2", robotName="successful robot", sort=2),
        ],
    )


@pytest.fixture
def reported_statuses(monkeypatch) -> list[TaskExecuteStatus]:
    statuses = []

    def fake_report_task_log(
        svc,
        status: TaskExecuteStatus,
        task_id=None,
        task_execute_id=None,
    ):
        statuses.append(status)
        if status == TaskExecuteStatus.EXECUTING:
            return "task-execution-1"
        return None

    monkeypatch.setattr(executor_module, "report_task_log", fake_report_task_log)
    monkeypatch.setattr(executor_module, "get_settings", lambda: {})
    monkeypatch.setattr(executor_module, "emit_to_front", MagicMock())

    return statuses


@pytest.mark.parametrize(
    ("retry_num", "expected_attempts"),
    [(0, 1), (1, 2), (2, 3)],
)
def test_retry_stop_stops_after_configured_retries(
    retry_num: int,
    expected_attempts: int,
    reported_statuses: list[TaskExecuteStatus],
) -> None:
    svc = make_svc(
        lambda **kwargs: make_executor(
            ExecuteStatus.FAIL,
            reason="recoverable failure",
        )
    )

    result = executor_run_list(make_task("retry_stop", retry_num), svc)
    created_projects = [
        call.kwargs["project_id"] for call in svc.executor_mg.create.call_args_list
    ]

    assert created_projects == ["robot-1"] * expected_attempts
    assert reported_statuses == [
        TaskExecuteStatus.EXECUTING,
        TaskExecuteStatus.EXEC_ERROR,
    ]
    assert "recoverable failure" in result["msg"]


@pytest.mark.parametrize(
    ("retry_num", "expected_attempts"),
    [(0, 1), (1, 2), (2, 3)],
)
def test_retry_jump_continues_after_configured_retries(
    retry_num: int,
    expected_attempts: int,
    reported_statuses: list[TaskExecuteStatus],
) -> None:
    def create_executor(**kwargs):
        if kwargs["project_id"] == "robot-1":
            return make_executor(
                ExecuteStatus.FAIL,
                reason="recoverable failure",
            )
        return make_executor(ExecuteStatus.SUCCESS)

    svc = make_svc(create_executor)

    result = executor_run_list(make_task("retry_jump", retry_num), svc)
    created_projects = [
        call.kwargs["project_id"] for call in svc.executor_mg.create.call_args_list
    ]

    assert created_projects == ["robot-1"] * expected_attempts + ["robot-2"]
    assert reported_statuses == [
        TaskExecuteStatus.EXECUTING,
        TaskExecuteStatus.SUCCESS,
    ]
    assert result["code"] == "0000"
    assert result["data"] == {}
