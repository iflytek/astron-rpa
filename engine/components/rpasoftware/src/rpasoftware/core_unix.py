from rpasoftware.core import ISoftwareCore


class SoftwareCore(ISoftwareCore):
    @staticmethod
    def get_app_path(app_name: str = "") -> str:
        raise NotImplementedError
