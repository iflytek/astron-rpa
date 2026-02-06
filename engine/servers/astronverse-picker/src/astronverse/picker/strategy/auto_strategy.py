import traceback
from _ctypes import COMError
from typing import TYPE_CHECKING, Optional

from astronverse.picker import APP, MSAA_APPLICATIONS, IElement
from astronverse.picker.engines.uia_picker import UIAOperate
from astronverse.picker.logger import logger

if TYPE_CHECKING:
    from astronverse.picker.strategy.types import Strategy, StrategySvc
    from astronverse.picker.svc import ServiceContext


def auto_default_strategy(
    service: "ServiceContext", strategy: "Strategy", strategy_svc: "StrategySvc"
) -> Optional[IElement]:
    """自动选择策略"""

    # 延迟导入策略函数避免循环依赖
    from astronverse.picker.strategy.msaa_strategy import msaa_default_strategy
    from astronverse.picker.strategy.uia_strategy import uia_default_strategy
    from astronverse.picker.strategy.web_strategy import web_default_strategy

    try:
        from astronverse.picker.strategy.jab_strategy import jab_default_strategy
        from astronverse.picker.strategy.sap_default_strategy import sap_default_strategy
        from astronverse.picker.strategy.web_ie_strategy import web_ie_default_strategy
    except Exception as e:
        logger.info(f"拾取模块导入异常{e}")

    # 2. 获取可能的元素
    preliminary_element = None
    chrome_like_apps = [
        APP.Chrome,
        APP.Firefox,
        APP.Chrome360X,
        APP.Chrome360se,
        APP.Chrome360,
        APP.Edge,
        APP.IE,
        APP.Chromium,
    ]
    if strategy_svc.app in chrome_like_apps:
        # 1. 如果是浏览器优先使用浏览器获取
        try:
            try:
                web_control_result = UIAOperate().get_web_control(
                    strategy_svc.start_control,
                    strategy_svc.app,
                    strategy_svc.last_point,
                )
                is_document, menu_top, menu_left, hwnd = web_control_result
            except Exception as e:
                logger.error("堆栈信息:\n{}".format(traceback.format_exc()))
                return None

            if is_document:
                if strategy_svc.app == APP.IE:
                    try:
                        preliminary_element = web_ie_default_strategy(
                            service, strategy, strategy_svc, (is_document, menu_top, menu_left, hwnd)
                        )
                    except Exception as e:
                        logger.error(f"auto_default_strategy web_ie_picker error: {e} {traceback.extract_stack()}")
                        preliminary_element = None
                else:
                    web_cache = (is_document, menu_top, menu_left, hwnd)
                    preliminary_element = web_default_strategy(service, strategy_svc, web_cache)
                # web元素直接返回，不做兜底
                return preliminary_element
        except COMError as e:
            # 忽略所有 COM 调用错误
            logger.warning(f"忽略 COMError: {e}")
            logger.debug("COMError 堆栈信息:\n{}".format(traceback.format_exc()))
            return None
        except Exception as e:
            logger.error("堆栈信息:\n%s", traceback.format_exc())
            logger.error(f"auto_default_strategy web error: {e} {traceback.extract_stack()}")
            raise e
    elif strategy_svc.app.value in MSAA_APPLICATIONS:
        preliminary_element = msaa_default_strategy(strategy_svc)
    elif strategy_svc.app == APP.SAP:
        # 2. 判断是否是sap
        try:
            preliminary_element = sap_default_strategy(service, strategy, strategy_svc)
        except Exception as e:
            logger.error(f"auto_default_strategy sap_picker error: {e} {traceback.extract_stack()}")
    else:
        # 3. 如果不是浏览器就优先使用JAB
        try:
            preliminary_element = jab_default_strategy(service, strategy, strategy_svc)
        except Exception as e:
            logger.error(f"auto_default_strategy jab_picker error: {e} {traceback.extract_stack()}")

    # 3. 兜底使用uia
    uia_element = None
    try:
        uia_element = uia_default_strategy(strategy_svc)
    except Exception as e:
        logger.error("堆栈信息:\n%s", traceback.format_exc())
        logger.error(f"auto_default_strategy uia_picker error: {e} {traceback.extract_stack()}")

    # 4. 结果优先选取
    if uia_element is None and preliminary_element is not None:
        return preliminary_element
    if preliminary_element is None and uia_element is not None:
        return uia_element
    if uia_element is None and preliminary_element is None:
        return None
    # 优先使用面积小的，如果相同使用preliminary_element
    logger.info(
        "pk: uia %s preliminary %s",
        uia_element.rect().area(),
        preliminary_element.rect().area(),
    )
    if preliminary_element.rect().area() <= uia_element.rect().area():
        return preliminary_element
    else:
        return uia_element
