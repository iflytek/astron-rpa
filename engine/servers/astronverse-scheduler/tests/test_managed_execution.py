import concurrent.futures
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
        item.ins = SimpleNamespace(set_param=lambda *_: None)
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


def test_simultaneous_duplicate_executes_once_and_preserves_json(client):
    controller, manager = client
    request = command(controller)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        receipts = list(pool.map(controller.handle, [request] * 8))
    assert {receipt["executionId"] for receipt in receipts} == {request["executionId"]}
    result = observe(controller, request, lambda r: r.get("status") == "succeeded")
    assert result["result"] == manager.result
    assert len(manager.instances) == 1
    assert controller.handle({**request, "payload": {"params": {"zero": 1}}})["error"] == "IDEMPOTENCY_CONFLICT"


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


def test_late_engine_receipt_after_scheduler_restart_is_recovered(client, tmp_path, monkeypatch):
    import json

    controller, manager = client
    monkeypatch.setattr(controller, "_run", lambda *_: None)
    request = command(controller)
    controller.handle(request)
    controller._change("owner", request["executionId"], runId="real-run", startedAt="2025-12-31T23:59:59+00:00")
    restarted = ManagedExecution(manager, tmp_path, "https://self-hosted.example")
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
    assert recovered["status"] == "succeeded"
    assert recovered["result"] == {"zero": 0}
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
