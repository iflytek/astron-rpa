from no_config import Config


class AppSettings:
    """
    应用配置
    """

    app_name: str = "rpa-browser-connector"


class HttpSettings:
    """
    http配置
    """

    app_host: str = "0.0.0.0"
    app_port: int = 9082
    gateway_port: int = 8003


@Config(type=dict(app_settings=AppSettings, http_settings=HttpSettings))
class Config:
    """
    公共配置
    """

    app_settings: AppSettings = AppSettings()
    http_settings: HttpSettings = HttpSettings()
