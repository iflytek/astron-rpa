import concurrent.futures
import json
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
from uuid import uuid4

import pytest
from astronverse.scheduler.core.executor.executor import ExecuteStatus
from astronverse.scheduler.core.executor.managed_execution import ManagedExecution


class Manager:
    """Use real disposable processes to verify stop evidence and target isolation."""

    def __init__(self):
        self.instances = []
        self.seconds = 0.2
        self.result = {"zero": 0, "nested": [False, None, {"value": "literal"}]}

    def status(self):
        return any(item.ins.is_alive() for item in self.instances)

    def create(self, on_prepared, on_started, **kwargs):
        item = SimpleNamespace(
            exec_id=str(uuid4()),
            report_log_time=0,
            execute_status=ExecuteStatus.EXECUTE,
            execute_data=None,
            execute_reason=None,
            launched_at=None,
        )
        item.launch_params = {}
        item.ins = SimpleNamespace(set_param=lambda key, value: item.launch_params.__setitem__(key, value))
        on_prepared(item)
        proc = subprocess.Popen(
            [sys.executable, "-c", f"import time; time.sleep({self.seconds})"],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        item.proc = proc
        item.ins = SimpleNamespace(is_alive=lambda: proc.poll() is None, proc=proc)
        item.launched_at = time.time()
        self.instances.append(item)
        on_started(item)

        def finish():
            code = proc.wait()
            item.execute_status = ExecuteStatus.SUCCESS if code == 0 else ExecuteStatus.CANCEL
            item.execute_data = self.result
            item.report_log_time = -1

        threading.Thread(target=finish, daemon=True).start()
        return item

    def close(self, item):
        if item.ins.is_alive():
            item.proc.terminate()


@pytest.fixture
def client(tmp_path):
    manager = Manager()
    controller = ManagedExecution(manager, tmp_path, "https://self-hosted.example")
    yield controller, manager
    for item in manager.instances:
        if item.ins.is_alive():
            item.proc.kill()
        item.proc.wait(timeout=5)


def command(client, action="start", execution_id=None, **extra):
    return {
        "protocol": 1,
        "action": action,
        "owner": "owner",
        "clientId": client.client_id,
        "executionId": execution_id or str(uuid4()),
        "payload": {"projectId": "project", "version": 1, "params": {"zero": 0}},
        **extra,
    }


def observe(client, request, predicate, timeout=5):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        receipt = client.handle({**request, "action": "get"})
        if predicate(receipt):
            return receipt
        time.sleep(0.02)
    pytest.fail("Execution did not reach expected state")


def test_failed_file_preparation_does_not_launch(client, monkeypatch):
    from astronverse.scheduler.core.executor.managed_files import FileTransferError

    controller, manager = client

    def prepare(_):
        raise FileTransferError("OFFICE_UNAVAILABLE")

    monkeypatch.setattr(controller, "_file_workspace", lambda *args: SimpleNamespace(prepare=prepare))
    request = command(controller)
    request["payload"]["fileBundle"] = {"version": 1}
    controller.handle(request)
    receipt = observe(controller, request, lambda value: value["status"] == "failed")
    assert receipt["error"] == "OFFICE_UNAVAILABLE"
    assert manager.instances == []


@pytest.mark.parametrize("bound", [False, True])
def test_preparation_failure_is_terminal_only_before_durable_process_binding(client, monkeypatch, bound):
    controller, manager = client

    def fail(on_prepared, **kwargs):
        if bound:
            on_prepared(SimpleNamespace(exec_id="bound-run", ins=SimpleNamespace(set_param=lambda *a: None)))
        raise TimeoutError("synthetic preparation timeout")

    monkeypatch.setattr(manager, "create", fail)
    request = command(controller)
    controller.handle(request)
    receipt = observe(controller, request, lambda row: row["status"] == ("unknown" if bound else "failed"))
    assert not manager.instances
    assert receipt["runId"] == ("bound-run" if bound else None)
    assert receipt["error"] == ("EXECUTION_START_UNCONFIRMED" if bound else "EXECUTION_FAILED")
    assert controller.handle(request)["executionId"] == receipt["executionId"]


def test_file_result_is_uploaded_before_terminal_success(client, monkeypatch):
    controller, manager = client
    calls = []

    def finish(result):
        calls.append("upload")
        return {"data": result, "files": {"target": {"fileId": "opaque"}}}

    monkeypatch.setattr(
        controller,
        "_file_workspace",
        lambda *args: SimpleNamespace(prepare=lambda p: p, finish=finish, cleanup=lambda: None),
    )
    request = command(controller)
    request["payload"]["fileBundle"] = {"version": 1}
    controller.handle(request)
    receipt = observe(controller, request, lambda value: value["status"] == "succeeded")
    assert receipt["result"]["data"] == manager.result
    assert receipt["result"]["files"]["target"]["fileId"] == "opaque"
    assert calls == ["upload"]


def test_simultaneous_duplicate_executes_once_and_preserves_json(client):
    controller, manager = client
    request = command(controller)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        receipts = list(pool.map(controller.handle, [request] * 8))
    assert {receipt["executionId"] for receipt in receipts} == {request["executionId"]}
    result = observe(controller, request, lambda r: r.get("status") == "succeeded")
    assert result["result"] == manager.result
    assert len(manager.instances) == 1
    assert "wait_tip_ws" not in manager.instances[0].launch_params
    assert controller.handle({**request, "payload": {"params": {"zero": 1}}})["error"] == "IDEMPOTENCY_CONFLICT"


@pytest.mark.parametrize("outcome", ["succeeded", "failed", "missing", "secret"])
def test_risk_completion_uses_private_receipt_not_redacted_report(client, monkeypatch, outcome):
    controller, manager = client
    manager.seconds = 0.3
    manager.result = ""  # Business values and failure diagnostics were redacted.
    request = command(controller)
    request["payload"]["riskContract"] = {"version": 1}
    if outcome == "secret":
        request["payload"]["secretFields"] = ["value"]
    create = manager.create

    def start(**kwargs):
        item = create(**kwargs)
        if outcome != "missing":
            path = controller.result_path("owner", request["executionId"])
            path.write_text(
                json.dumps(
                    {
                        "runId": item.exec_id,
                        "status": "failed" if outcome == "failed" else "succeeded",
                        "result": None if outcome == "failed" else {"answer": "approved"},
                        "error": "RISK_ARGUMENTS_DENIED" if outcome == "failed" else None,
                        "processId": item.proc.pid,
                        "processStarted": __import__("psutil").Process(item.proc.pid).create_time(),
                        "startedAt": "2026-01-01T00:00:00+00:00",
                        "finishedAt": "2026-01-01T00:00:01+00:00",
                    }
                ),
                encoding="utf-8",
            )
        return item

    monkeypatch.setattr(manager, "create", start)
    controller.handle(request)
    expected = {"secret": "succeeded", "missing": "unknown"}.get(outcome, outcome)
    receipt = observe(controller, request, lambda row: row["status"] == expected)
    assert receipt["supportsCancel"] is False
    assert receipt.get("result") == ({"answer": "approved"} if outcome == "succeeded" else None)
    if outcome == "failed":
        assert receipt["error"] == "RISK_ARGUMENTS_DENIED"
    if outcome == "missing":
        assert receipt["error"] == "EXECUTION_OBSERVATION_FAILED"


def test_busy_cancel_old_id_and_wrong_run_never_stop_new_task(client):
    controller, manager = client
    manager.seconds = 10
    first = command(controller)
    controller.handle(first)
    running = observe(controller, first, lambda r: r.get("status") == "running")
    rejected = command(controller)
    assert controller.handle(rejected)["error"] == "CLIENT_BUSY"
    bad = {**first, "action": "cancel", "runId": "wrong-run"}
    assert controller.handle(bad)["error"] == "EXECUTION_TARGET_MISMATCH"
    assert manager.instances[0].ins.is_alive()
    cancel = {**first, "action": "cancel", "runId": running["runId"]}
    assert controller.handle(cancel)["cancelRequested"]
    ended = observe(controller, first, lambda r: r.get("status") == "cancelled")
    assert ended["finishedAt"]
    assert not manager.instances[0].ins.is_alive()
    second = command(controller)
    controller.handle(second)
    observe(controller, second, lambda r: r.get("status") == "running")
    assert controller.handle(cancel)["status"] == "cancelled"
    assert manager.instances[1].ins.is_alive()
    assert controller.handle(rejected)["error"] == "CLIENT_BUSY"  # Rejected receipt is never queued.


def test_execution_deadline_has_real_process_stop_evidence(client):
    controller, manager = client
    manager.seconds = 10
    request = command(controller)
    request["payload"]["executionTimeout"] = 1
    controller.handle(request)
    result = observe(controller, request, lambda r: r.get("status") == "timeout")
    assert result["startedAt"]
    assert result["finishedAt"]
    assert not manager.instances[0].ins.is_alive()


def test_restart_uncertain_receipt_never_replays_and_owner_isolation(client, tmp_path, monkeypatch):
    controller, manager = client
    monkeypatch.setattr(controller, "_run", lambda *_: None)  # Crash after receipt commit, before launch.
    request = command(controller)
    controller.handle(request)
    restarted = ManagedExecution(manager, tmp_path, "https://self-hosted.example")
    assert restarted.client_id == controller.client_id
    receipt = restarted.handle(request)
    assert receipt["status"] == "unknown"
    assert not receipt["supportsCancel"]
    assert manager.instances == []
    assert restarted.handle({**request, "action": "get", "owner": "other"})["error"] == "EXECUTION_NOT_FOUND"
    other_origin = ManagedExecution(manager, tmp_path, "https://another.example")
    assert other_origin.client_id != controller.client_id
    assert other_origin.handle(request)["error"] == "EXECUTION_TARGET_MISMATCH"


def test_durable_terminal_result_survives_restart_and_objects_are_rejected(client, tmp_path):
    controller, manager = client
    manager.result = object()
    request = command(controller)
    controller.handle(request)
    result = observe(controller, request, lambda r: r.get("status") == "failed")
    assert result["error"] == "UNSUPPORTED_RESULT"
    restarted = ManagedExecution(manager, tmp_path, "https://self-hosted.example")
    assert restarted.handle(request) == result
    assert len(manager.instances) == 1


def test_secret_payload_not_in_journal_or_public_result(client):
    controller, _ = client
    request = command(controller)
    request["payload"].update(params={"secret": "sensitive-fixture"}, secretFields=["secret"])
    controller.handle(request)
    result = observe(controller, request, lambda r: r.get("status") == "succeeded")
    assert result["result"] is None
    assert b"sensitive-fixture" not in controller.path.read_bytes()


@pytest.mark.parametrize("desktop_error", [None, "DESKTOP_LOCKED"])
def test_late_engine_receipt_after_scheduler_restart_is_recovered(client, tmp_path, monkeypatch, desktop_error):
    import json

    controller, manager = client
    monkeypatch.setattr(controller, "_run", lambda *_: None)
    request = command(controller)
    controller.handle(request)
    controller._change("owner", request["executionId"], runId="real-run", startedAt="2025-12-31T23:59:59+00:00")
    if desktop_error:
        controller._change("owner", request["executionId"], desktopError=desktop_error, fileWorkflow=True)
    restarted = ManagedExecution(manager, tmp_path, "https://self-hosted.example")
    monkeypatch.setattr(restarted, "_cleanup_files", lambda *_: None)
    monkeypatch.setattr(restarted, "_file_workspace", lambda *_: pytest.fail("Interrupted output must not upload"))
    assert restarted.handle({**request, "action": "get"})["status"] == "unknown"
    path = restarted.result_path("owner", request["executionId"])
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "runId": "wrong-run",
        "status": "succeeded",
        "result": {"zero": 0},
        "processId": 999999999,
        "processStarted": 1,
        "startedAt": "2026-01-01T00:00:00+00:00",
        "finishedAt": "2026-01-01T00:00:01+00:00",
    }
    path.write_text(json.dumps(payload))
    assert restarted.handle({**request, "action": "get"})["status"] == "unknown"
    path.write_text(json.dumps({**payload, "runId": "real-run"}))
    recovered = restarted.handle({**request, "action": "get"})
    assert recovered["status"] == ("failed" if desktop_error else "succeeded")
    assert recovered["result"] == (None if desktop_error else {"zero": 0})
    if desktop_error:
        assert recovered["error"] == desktop_error
    assert recovered["startedAt"] == "2025-12-31T23:59:59+00:00"
    assert manager.instances == []


def test_cancellation_during_preparation_never_launches(client, monkeypatch):
    controller, manager = client
    entered, release = threading.Event(), threading.Event()
    create = manager.create

    def prepare(**kwargs):
        entered.set()
        assert release.wait(3)
        return create(**kwargs)

    monkeypatch.setattr(manager, "create", prepare)
    request = command(controller)
    controller.handle(request)
    assert entered.wait(3)
    assert controller.handle({**request, "action": "cancel", "runId": None})["cancelRequested"]
    release.set()
    observe(controller, request, lambda r: r["status"] == "cancelled")
    assert manager.instances == []


@pytest.mark.parametrize("raises", [False, True])
def test_failed_stop_is_unconfirmed_and_late_success_remains_success(client, monkeypatch, raises):
    from astronverse.scheduler.core.executor import managed_execution

    controller, manager = client
    manager.seconds = 1
    monkeypatch.setattr(managed_execution, "STOP_CONFIRMATION_SECONDS", 0.05)

    def unavailable(_):
        if raises:
            raise OSError("stop unavailable")

    monkeypatch.setattr(manager, "close", unavailable)
    request = command(controller)
    controller.handle(request)
    running = observe(controller, request, lambda r: r["status"] == "running")
    controller.handle({**request, "action": "cancel", "runId": running["runId"]})
    uncertain = observe(controller, request, lambda r: r["status"] == "unknown")
    assert uncertain["error"] == "STOP_UNCONFIRMED"
    assert not uncertain["supportsCancel"]
    assert manager.instances[0].ins.is_alive()
    observe(controller, request, lambda r: r["status"] == "succeeded")


def test_deadline_runs_while_manager_waits_for_startup(client, monkeypatch):
    controller, manager = client
    manager.seconds = 10
    create = manager.create
    release = threading.Event()

    def slow_ready(**kwargs):
        instance = create(**kwargs)
        release.wait(3)
        return instance

    monkeypatch.setattr(manager, "create", slow_ready)
    request = command(controller)
    request["payload"]["executionTimeout"] = 1
    controller.handle(request)
    try:
        observe(controller, request, lambda r: r["status"] == "timeout", timeout=2)
        assert not manager.instances[0].ins.is_alive()
    finally:
        release.set()


def test_restarted_scheduler_blocks_new_external_run_while_orphan_lives(client, tmp_path, monkeypatch):
    controller, manager = client
    manager.seconds = 10
    request = command(controller)
    controller.handle(request)
    observe(controller, request, lambda r: r["status"] == "running")
    empty_manager = Manager()
    restarted = ManagedExecution(empty_manager, tmp_path, "https://self-hosted.example")
    assert restarted.handle(command(restarted))["error"] == "CLIENT_BUSY"
    assert empty_manager.instances == []


def test_file_recovery_does_not_hold_lock_during_transfer(client, tmp_path, monkeypatch):
    controller, _ = client
    monkeypatch.setattr(controller, "_run", lambda *_: None)
    request = command(controller)
    request["payload"]["fileBundle"] = {"version": 1}
    controller.handle(request)
    controller._change("owner", request["executionId"], status="unknown", runId="run-1")
    controller.active.clear()  # Simulate the absence of a live observer after restart.
    path = controller.result_path("owner", request["executionId"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "runId": "run-1",
                "status": "succeeded",
                "result": {"value": 0},
                "processId": 999999999,
                "processStarted": 1,
                "startedAt": "2026-01-01T00:00:00+00:00",
                "finishedAt": "2026-01-01T00:00:01+00:00",
            }
        )
    )
    entered, release = threading.Event(), threading.Event()

    class Workspace:
        def finish(self, result):
            entered.set()
            assert release.wait(3)
            return {"data": result, "files": {}}

        def cleanup(self):
            pass

    monkeypatch.setattr(controller, "_file_workspace", lambda *_: Workspace())
    result = {}
    thread = threading.Thread(
        target=lambda: result.setdefault("receipt", controller.handle({**request, "action": "get"}))
    )
    thread.start()
    assert entered.wait(3)
    started = time.monotonic()
    concurrent = controller.handle({**request, "action": "get"})
    assert time.monotonic() - started < 0.5
    assert concurrent["status"] == "unknown"
    started = time.monotonic()
    assert controller.handle(command(controller))["error"] == "CLIENT_BUSY"
    assert time.monotonic() - started < 0.5
    release.set()
    thread.join(timeout=3)
    assert result["receipt"]["status"] == "succeeded"


@pytest.mark.parametrize("code", ["DESKTOP_LOCKED", "DESKTOP_RESOLUTION_MISMATCH", "DESKTOP_SOFTWARE_UNAVAILABLE"])
def test_desktop_preflight_failure_never_launches_or_replays(client, monkeypatch, code):
    from astronverse.scheduler.core.executor import managed_desktop

    controller, manager = client

    def unavailable(*_, **__):
        raise managed_desktop.DesktopError(code)

    monkeypatch.setattr(managed_desktop, "DesktopGuard", lambda _: SimpleNamespace(check=unavailable))
    request = command(controller)
    request["payload"].update(desktopContract={"version": 1}, executionTimeout=10)
    controller.handle(request)
    failed = observe(controller, request, lambda r: r["status"] == "failed")
    assert failed["error"] == code
    assert not manager.instances
    assert controller.handle(request)["executionId"] == failed["executionId"]
    assert not manager.instances


def test_desktop_session_loss_stops_exact_process_and_preserves_failure(client, monkeypatch):
    from astronverse.scheduler.core.executor import managed_desktop

    controller, manager = client
    manager.seconds = 10
    lost = threading.Event()

    def check(**_):
        if lost.is_set():
            raise managed_desktop.DesktopError("DESKTOP_LOCKED")

    monkeypatch.setattr(managed_desktop, "DesktopGuard", lambda _: SimpleNamespace(check=check))
    request = command(controller)
    request["payload"].update(desktopContract={"version": 1}, executionTimeout=10)
    controller.handle(request)
    running = observe(controller, request, lambda r: r["status"] == "running")
    assert controller.handle(command(controller))["error"] == "CLIENT_BUSY"
    assert manager.instances[0].launch_params["wait_tip_ws"] == "n"
    assert manager.instances[0].launch_params["managed_desktop"] == "y"
    lost.set()
    failed = observe(controller, request, lambda r: r["status"] == "failed")
    assert failed["error"] == "DESKTOP_LOCKED"
    assert failed["runId"] == running["runId"]
    assert not manager.instances[0].ins.is_alive()
