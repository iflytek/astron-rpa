from astronverse.scheduler.core.svc import get_svc


def test_legacy_core_alias_points_to_scheduler_port():
    svc = get_svc()

    assert svc.port_dict["core"] == svc.scheduler_port
    assert svc.port_dict["scheduler"] == svc.scheduler_port
