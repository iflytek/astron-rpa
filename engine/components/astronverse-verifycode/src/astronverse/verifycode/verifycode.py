import time

import pyautogui
from astronverse.actionlib import DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import WebPick
from astronverse.baseline.logger.logger import logger
from astronverse.browser.browser import Browser
from astronverse.browser.browser_element import BrowserElement
from astronverse.locator import smooth_move
from astronverse.locator.locator import locator
from astronverse.verifycode import HintPosition, PictureCodeType
from astronverse.verifycode.core import VerifyCodeCore
from astronverse.verifycode.error import *

VerifyCodeCore = VerifyCodeCore()
Locator = locator


class VerifyCode:
    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "input_box",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_box.show",
                        expression="return  $this.input_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("code_result", types="Str"),
        ],
    )
    def picture_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        code_type: PictureCodeType = PictureCodeType.GENERAL1234,
        input_flag: bool = False,
        input_box: WebPick = None,
    ) -> str:
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())
        code_result = VerifyCodeCore.get_api_result(api_type=code_type.value, pic_element_base64=image_base64)
        logger.info("验证码返回值: {}".format(code_result))
        if not code_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        if input_flag:
            BrowserElement.input(browser_obj=browser_obj, element_data=input_box, fill_input=code_result)

        return code_result

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "move_pic_pick",
                dynamics=[
                    DynamicsItem(
                        key="$this.move_pic_pick.show",
                        expression="return  $this.unmatched_flag.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "mini_step",
                dynamics=[
                    DynamicsItem(
                        key="$this.mini_step.show",
                        expression="return  $this.unmatched_flag.value == true",
                    )
                ],
            ),
            atomicMg.param("offset", required=False),
        ],
        outputList=[atomicMg.param("drag_distance", types="Int")],
    )
    def slider_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        slider_pick: WebPick = None,
        unmatched_flag: bool = False,
        move_pic_pick: WebPick = None,
        mini_step: int = 5,
        offset: int = 0,
    ) -> int:
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())
        drag_distance = int(VerifyCodeCore.get_api_result(api_type="22222", pic_element_base64=image_base64))
        logger.info("验证码返回值: {}".format(drag_distance))
        drag_distance = drag_distance + offset
        logger.info("加入偏移量之后的移动量: {}".format(drag_distance))
        if not drag_distance:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        slider_element = Locator.locator(slider_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        if isinstance(slider_element.rect(), list):
            raise BizException(ELEMENT_NOT_UNIQUE, "浏览器元素定位不唯一，请检查！")
        start_pos = slider_element.point()
        if not unmatched_flag:
            end_pos = (start_pos.x + drag_distance, start_pos.y)
            VerifyCodeCore.html_drag_plus(start_pos, end_pos)

        else:
            smooth_move(start_pos.x, start_pos.y, duration=0.5)
            pyautogui.mouseDown()
            smooth_move(start_pos.x + drag_distance * 0.85, start_pos.y, duration=0.5)
            time.sleep(0.5)
            delta = drag_distance - round(float(VerifyCodeCore.get_margin_left(browser_obj, move_pic_pick)))
            logger.info(delta)
            while abs(delta) > mini_step:
                if delta > 0:
                    smooth_move(pyautogui.position().x + mini_step, start_pos.y, duration=0.5)
                    # pyautogui.moveTo(pyautogui.position().x + mini_step, start_pos.y, duration=0.5)
                else:
                    smooth_move(pyautogui.position().x - mini_step, start_pos.y, duration=0.5)
                    # pyautogui.moveTo(pyautogui.position().x - mini_step, start_pos.y, duration=0.5)
                time.sleep(0.5)
                delta = drag_distance - round(float(VerifyCodeCore.get_margin_left(browser_obj, move_pic_pick)))
                logger.info(delta)
            # 释放滑块
            pyautogui.mouseUp()

        return drag_distance

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def click_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        hint_position: HintPosition = HintPosition.BOTTOM,
    ):
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 86,94|255,62|170,92
        click_result = VerifyCodeCore.get_api_result(
            api_type="30332",
            pic_element_base64=image_base64,
            direction=hint_position.value,
        )
        logger.info("验证码返回值: {}".format(click_result))
        if not click_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")
        click_positions = click_result.split("|")
        click_positions = [tuple(map(int, pos.split(","))) for pos in click_positions]

        # 开始点击
        for pos in click_positions:
            pos = (pos[0] + rect.left, pos[1] + rect.top)
            smooth_move(*pos, duration=0.5)
            pyautogui.click()
            time.sleep(0.5)

        return click_positions

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("hint_text_pick", required=True),
            atomicMg.param("refresh_pick", required=True),
            atomicMg.param("slider_pick", required=True),
            atomicMg.param("background_pic_pick", required=True),
        ],
        outputList=[atomicMg.param("drag_distance", types="Int")],
    )
    def ali_slider_code(
        browser_obj: Browser = None,
        hint_text_pick: WebPick = None,
        refresh_pick: WebPick = None,
        slider_pick: WebPick = None,
        background_pic_pick: WebPick = None,
    ) -> int:
        """阿里滑块验证码识别

        Args:
            browser_obj: 浏览器对象
            hint_text_pick: 提示文字元素
            slider_pick: 待拖动的滑块元素
            background_pic_pick: 背景图片元素

        Returns:
            int: 滑块需要向右拖动的像素距离
        """
        # response = browser_obj.send_browser_extension(
        #     browser_type=browser_obj.browser_type.value,
        #     key= 'setRequestInterceptionFilters',
        #     data= [{
        #         "urlPattern": 'https://zhaoshang.tmall.com',
        #         "pathPattern": '/maintaininfo/liangzhao.htm/_____tmd_____/newslidecaptcha',
        #         "method" : 'GET'
        #     }]
        # )
        response = browser_obj.send_browser_extension(
            browser_type=browser_obj.browser_type.value,
            key="startDebugNetworkListen",
            data=[
                {
                    "urlPattern": "https://zhaoshang.tmall.com",
                    "pathPattern": "/maintaininfo/liangzhao.htm/_____tmd_____/newslidecaptcha",
                }
            ],
        )
        # 通过插件获取网络数据
        max_retries = 5
        response = None

        for retry_count in range(1, max_retries + 1):
            # 点击刷新按钮
            refresh_element = Locator.locator(
                refresh_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value
            )
            refresh_pos = refresh_element.point()
            smooth_move(refresh_pos.x, refresh_pos.y, duration=0.5)
            pyautogui.click()
            logger.info("第 {} 次点击刷新按钮".format(retry_count))

            # 等待 n 秒（从1秒开始递增）
            wait_time = retry_count + 3
            logger.info("等待 {} 秒后获取网络数据".format(wait_time))
            time.sleep(wait_time)

            # 通过插件获取网络数据
            response = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value, key="getDebugNetworkData", data={}
            )

            logger.info("第 {} 次获取到的网络数据响应: {}".format(retry_count, response))

            # 检查响应是否为空
            if response and len(response) > 0:
                logger.info("成功获取到网络数据，退出重试")
                break
            else:
                logger.info("响应为空，继续重试")
                if retry_count == max_retries:
                    raise BizException(API_RESULT_EMPTY, "重试 {} 次后插件返回数据仍为空".format(max_retries))

        # 从响应中提取两张图片的base64数据
        if not response:
            raise BizException(API_RESULT_EMPTY, "插件返回数据为空")
        data = response[-1].get("responseBody", {}).get("data", {})
        image_data_base64 = data.get("imageData", "")
        ques_base64 = data.get("ques", "")

        if not image_data_base64 or not ques_base64:
            raise BizException(API_RESULT_EMPTY, "图片数据为空")

        # 去除base64前缀（如果有）
        if "," in image_data_base64:
            image_data_base64 = image_data_base64.split(",", 1)[1]
        if "," in ques_base64:
            ques_base64 = ques_base64.split(",", 1)[1]

        # 解码base64图片
        image_data_bytes = base64.b64decode(image_data_base64)
        ques_bytes = base64.b64decode(ques_base64)

        # 使用PIL打开图片
        image_data_img = Image.open(BytesIO(image_data_bytes))
        ques_img = Image.open(BytesIO(ques_bytes))

        # 如果图片有透明通道（RGBA），转换为RGB模式，透明部分填充白色
        if image_data_img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", image_data_img.size, (255, 255, 255))
            if image_data_img.mode == "P":
                image_data_img = image_data_img.convert("RGBA")
            bg.paste(image_data_img, mask=image_data_img.split()[-1] if image_data_img.mode == "RGBA" else None)
            image_data_img = bg

        if ques_img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", ques_img.size, (255, 255, 255))
            if ques_img.mode == "P":
                ques_img = ques_img.convert("RGBA")
            bg.paste(ques_img, mask=ques_img.split()[-1] if ques_img.mode == "RGBA" else None)
            ques_img = bg

        # 记录背景图原始宽度（用于后续比例计算）
        bg_img_width = image_data_img.width
        logger.info("背景图尺寸: {}, 问题图尺寸: {}".format(image_data_img.size, ques_img.size))

        # 拼接图片（垂直拼接，问题图在上，背景图在下）
        total_width = max(image_data_img.width, ques_img.width)
        total_height = image_data_img.height + ques_img.height

        # 创建新图片（白色背景）
        combined_img = Image.new("RGB", (total_width, total_height), (255, 255, 255))

        # 粘贴问题图（上方）
        combined_img.paste(ques_img, (0, 0))

        # 粘贴背景图（下方）
        combined_img.paste(image_data_img, (0, ques_img.height))

        # 保存拼接后的图片
        combined_img.save("阿里滑块.jpg")
        logger.info("拼接后的图片已保存为: 阿里滑块.jpg")

        # 将拼接后的图片转换为base64
        buffered = BytesIO()
        combined_img.save(buffered, format="JPEG")
        combined_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # 调用第三方API识别滑块距离，返回值为图片上满足要求的像素点x坐标
        pixel_x = int(VerifyCodeCore.get_api_result(api_type="20226", pic_element_base64=combined_base64))
        logger.info("云码返回像素点x: {}".format(pixel_x))

        if not pixel_x:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 获取背景图元素在页面上显示的实际宽度
        bg_element = Locator.locator(
            background_pic_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value
        )
        bg_rect = bg_element.rect()
        element_width = bg_rect.width()

        # 获取滑块宽度（用于修正拖动距离）
        slider_element = Locator.locator(slider_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        if isinstance(slider_element.rect(), list):
            raise BizException(ELEMENT_NOT_UNIQUE, "滑块元素定位不唯一，请检查！")
        slider_rect = slider_element.rect()
        slider_width = slider_rect.width()

        # 按比例将图片像素x转换为实际拖动距离，减去滑块一半宽度（因为拼图块通常在滑块中心）
        drag_distance = int(pixel_x / bg_img_width * element_width - slider_width / 2)
        logger.info(
            "图片宽度: {}px, 元素宽度: {}px, 滑块宽度: {}px, 像素x: {}, 计算拖动距离: {}px".format(
                bg_img_width, element_width, slider_width, pixel_x, drag_distance
            )
        )

        # 拖动滑块（自定义拖动逻辑，无过冲回调）
        start_pos = slider_element.point()
        end_pos = (start_pos.x + drag_distance, start_pos.y)

        # 执行拖动：移动到起点 -> 按下 -> 分段移动到终点 -> 释放
        import random

        smooth_move(start_pos.x, start_pos.y, duration=0.5)
        pyautogui.mouseDown(start_pos.x, start_pos.y, button="left")
        time.sleep(0.5)

        # 分段移动模拟人类行为
        distance = drag_distance
        pos_1 = (start_pos.x + distance * 0.7, start_pos.y + 10)
        smooth_move(*pos_1, duration=random.choice([0.2, 0.4, 0.6]))

        pos_2 = (start_pos.x + distance * 0.9, start_pos.y + 10)
        smooth_move(*pos_2, duration=random.choice([0.2, 0.4, 0.6]))

        # 最终移动到目标位置
        smooth_move(*end_pos, duration=0.2)
        pyautogui.mouseUp(*end_pos, button="left")

        logger.info("阿里滑块拖动完成，从 {} 到 {}".format(start_pos, end_pos))

        # 停止网络监听
        browser_obj.send_browser_extension(
            browser_type=browser_obj.browser_type.value, key="stopDebugNetworkListen", data={}
        )
        logger.info("已停止网络监听")

        return drag_distance

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("picture_pick", required=True),
            atomicMg.param("confirm_button_pick", required=True),
        ],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def text_click_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        confirm_button_pick: WebPick = None,
    ):
        """通用文字点选验证码（按语序点击）

        Args:
            browser_obj: 浏览器对象
            picture_pick: 待识别的点选背景图对象
            confirm_button_pick: 确定按钮对象

        Returns:
            list: 点击位置信息列表，每个元素包含坐标、文字和顺序
        """
        # 获取背景图片元素并截图
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("背景图rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 调用第三方API识别文字位置（使用文字点选验证码类型）
        click_result = VerifyCodeCore.get_api_result(
            api_type="30116",
            pic_element_base64=image_base64,
        )
        logger.info("文字点选验证码返回值: {}".format(click_result))

        if not click_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 解析返回结果，格式示例: "328,200|342,322|414,215|111,142"
        click_positions = []
        for item in click_result.split("|"):
            parts = item.split(",")
            if len(parts) >= 2:
                click_positions.append({"x": int(parts[0]), "y": int(parts[1])})

        # 按顺序点击文字位置
        for pos_info in click_positions:
            # 计算绝对坐标
            abs_x = pos_info["x"] + rect.left
            abs_y = pos_info["y"] + rect.top
            logger.info("点击文字  位置: ({}, {})".format(abs_x, abs_y))
            smooth_move(abs_x, abs_y, duration=0.5)
            pyautogui.click()
            time.sleep(0.5)

        # 点击确定按钮
        confirm_element = Locator.locator(
            confirm_button_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value
        )
        confirm_pos = confirm_element.point()
        logger.info("点击确定按钮位置: ({}, {})".format(confirm_pos.x, confirm_pos.y))
        smooth_move(confirm_pos.x, confirm_pos.y, duration=0.5)
        pyautogui.click()

        return click_positions

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("picture_pick", required=True),
            atomicMg.param("confirm_button_pick", required=True),
        ],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def spatial_reasoning_click_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        confirm_button_pick: WebPick = None,
    ):
        """空间推理点选验证码（相同物体）

        Args:
            browser_obj: 浏览器对象
            picture_pick: 待识别的点选背景图对象
            confirm_button_pick: 确定按钮对象

        Returns:
            list: 点击位置信息列表，每个元素包含坐标、物体类型、颜色、大小、原因等属性
        """
        # 获取背景图片元素并截图
        element = Locator.locator(picture_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("背景图rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 调用第三方API识别符合空间推理条件的物体（使用空间推理验证码类型）
        click_result = VerifyCodeCore.get_api_result(
            api_type="30101",
            pic_element_base64=image_base64,
        )
        logger.info("空间推理点选验证码返回值: {}".format(click_result))

        if not click_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 解析返回结果，格式示例: "280,297|181,152"
        click_positions = []
        for item in click_result.split("|"):
            parts = item.split(",")
            if len(parts) >= 2:
                position_info = {
                    "x": int(parts[0]),
                    "y": int(parts[1]),
                }
                click_positions.append(position_info)

        # 依次点击识别出的物体位置
        for pos_info in click_positions:
            # 计算绝对坐标
            abs_x = pos_info["x"] + rect.left
            abs_y = pos_info["y"] + rect.top
            logger.info("点击物体位置: ({}, {}), 属性: {}".format(abs_x, abs_y, pos_info))
            smooth_move(abs_x, abs_y, duration=0.5)
            pyautogui.click()
            time.sleep(0.5)

        # 点击确定按钮
        confirm_element = Locator.locator(
            confirm_button_pick.get("elementData"), cur_target_app=browser_obj.browser_type.value
        )
        confirm_pos = confirm_element.point()
        logger.info("点击确定按钮位置: ({}, {})".format(confirm_pos.x, confirm_pos.y))
        smooth_move(confirm_pos.x, confirm_pos.y, duration=0.5)
        pyautogui.click()

        return click_positions

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("prompt_obj", required=True),
            atomicMg.param("background_img_obj", required=True),
            atomicMg.param("confirm_button_obj", required=True),
        ],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def tencent_grid_click_code(
        browser_obj: Browser = None,
        prompt_obj: WebPick = None,
        background_img_obj: WebPick = None,
        confirm_button_obj: WebPick = None,
    ):
        """腾讯六宫格验证码（腾讯六图/图标点选验证码）

        Args:
            browser_obj: 浏览器对象
            prompt_obj: 提示对象，验证码补充提示词（例如"请点击所有的苹果"）
            background_img_obj: 背景图片对象，待识别处理图片
            confirm_button_obj: 确定按钮对象

        Returns:
            list: 点击位置信息列表，每个元素包含坐标、网格索引、标签等信息
        """
        if not prompt_obj:
            raise BizException(PARAM_INVALID, "提示对象是必填的")

        # 获取背景图片元素并截图
        element = Locator.locator(background_img_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("腾讯六宫格背景图rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())
        # 保存为 test123.jpg
        import base64

        with open("test123.jpg", "wb") as f:
            f.write(base64.b64decode(image_base64))

        prompt_text = BrowserElement.element_text(browser_obj=browser_obj, element_data=prompt_obj, element_timeout=10)
        logger.info("腾讯六宫格提示词: {}".format(prompt_text))
        # 调用第三方API识别六宫格验证码（使用腾讯六宫格验证码类型）
        # 传入extra参数作为提示词
        click_result = VerifyCodeCore.get_api_result(
            api_type="30221",
            pic_element_base64=image_base64,
            extra=prompt_text,
        )
        logger.info("腾讯六宫格验证码返回值: {}".format(click_result))

        if not click_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 解析返回结果，格式示例: "120,180|320,420"
        click_positions = []
        for item in click_result.split("|"):
            parts = item.split(",")
            if len(parts) >= 2:
                position_info = {
                    "x": int(parts[0]),
                    "y": int(parts[1]),
                }

                click_positions.append(position_info)

        # 依次点击识别出的位置
        for pos_info in click_positions:
            # 计算绝对坐标
            abs_x = pos_info["x"] + rect.left
            abs_y = pos_info["y"] + rect.top
            logger.info("点击位置: ({}, {})".format(abs_x, abs_y))
            smooth_move(abs_x, abs_y, duration=0.5)
            pyautogui.click()
            time.sleep(0.5)

        # 点击确定按钮
        confirm_element = Locator.locator(
            confirm_button_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value
        )
        confirm_pos = confirm_element.point()
        logger.info("点击确定按钮位置: ({}, {})".format(confirm_pos.x, confirm_pos.y))
        smooth_move(confirm_pos.x, confirm_pos.y, duration=0.5)
        pyautogui.click()

        return click_positions

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("rotate_picture_obj", required=True),
            atomicMg.param("slider_obj", required=True),
            atomicMg.param("slide_bar_obj", required=True),
            atomicMg.param(
                "max_rotate_angle", required=True, formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value)
            ),
        ],
        outputList=[],
    )
    def rotate_slider_code(
        browser_obj: Browser = None,
        rotate_picture_obj: WebPick = None,
        slider_obj: WebPick = None,
        slide_bar_obj: WebPick = None,
        max_rotate_angle: MaxRotateAngle = MaxRotateAngle.ANGLE_360,
    ):
        """通用旋转验证码（滑块拖动旋转）

        Args:
            browser_obj: 浏览器对象
            rotate_picture_obj: 旋转图片对象（待旋转的图片）
            slider_obj: 滑块对象（待拖动的滑块元素）
            slide_bar_obj: 滑动条对象（完整的滑动条元素，用于计算可拖动距离）
            max_rotate_angle: 图片旋转最大角度（滑动条拉到尽头后图片的旋转角度），可选360°或180°
        """
        # 获取旋转图片元素并截图
        rotate_element = Locator.locator(
            rotate_picture_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value
        )
        rotate_rect = rotate_element.rect()
        logger.info("旋转图片rect: {}".format(rotate_rect))
        rotate_image_base64 = VerifyCodeCore.get_base64_screenshot(
            rotate_rect.left, rotate_rect.top, rotate_rect.width(), rotate_rect.height()
        )

        # 调用第三方API识别旋转角度（使用旋转验证码类型）
        rotate_angle = int(VerifyCodeCore.get_api_result(api_type="900011", pic_element_base64=rotate_image_base64))
        logger.info("旋转验证码返回旋转角度: {}".format(rotate_angle))

        if rotate_angle is None:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 获取滑动条元素，计算可拖动距离
        slide_bar_element = Locator.locator(
            slide_bar_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value
        )
        slide_bar_rect = slide_bar_element.rect()

        # 获取滑块元素
        slider_element = Locator.locator(slider_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        if isinstance(slider_element.rect(), list):
            raise BizException(ELEMENT_NOT_UNIQUE, "滑块元素定位不唯一，请检查！")

        slider_start_pos = slider_element.point()

        # 计算滑动距离：根据旋转角度和最大旋转角度计算
        max_angle = int(max_rotate_angle.value)
        slide_bar_width = slide_bar_rect.width()
        drag_distance = int((rotate_angle / max_angle) * slide_bar_width)

        logger.info(
            "最大旋转角度: {}°, 需要旋转角度: {}°, 滑动条宽度: {}px, 计算拖动距离: {}px".format(
                max_angle, rotate_angle, slide_bar_width, drag_distance
            )
        )

        # 执行拖动操作
        end_pos = (slider_start_pos.x + drag_distance, slider_start_pos.y)
        VerifyCodeCore.html_drag_plus(slider_start_pos, end_pos)

        logger.info("旋转验证码拖动完成")

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("out_ring_image_obj", required=True),
            atomicMg.param("inner_circle_image_obj", required=True),
            atomicMg.param("slider_obj", required=True),
            atomicMg.param("slide_bar_obj", required=True),
            atomicMg.param(
                "max_rotate_angle",
                required=True,
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                tip="滑动条拉到尽头后内圈的旋转角度",
            ),
        ],
        outputList=[],
    )
    def double_ring_rotate_code(
        browser_obj: Browser = None,
        out_ring_image_obj: WebPick = None,
        inner_circle_image_obj: WebPick = None,
        slider_obj: WebPick = None,
        slide_bar_obj: WebPick = None,
        max_rotate_angle: MaxRotateAngle = MaxRotateAngle.ANGLE_360,
    ):
        """通用双圈旋转验证码（内圈外圈旋转）

        Args:
            browser_obj: 浏览器对象
            out_ring_image_obj: 外圈图片对象
            inner_circle_image_obj: 内圈图片对象
            slider_obj: 滑块对象（待拖动的滑块元素）
            slide_bar_obj: 滑动条对象（完整的滑动条元素）
            max_rotate_angle: 图片旋转最大角度（滑动条拉到尽头后内圈的旋转角度），可选360°或180°
        """
        # 获取外圈图片元素并截图

        src_url = BrowserElement.element_operation(
            browser_obj=browser_obj,
            element_data=out_ring_image_obj,  # 已拾取的 img 元素
            operation_type=ElementAttributeOpTypeFlag.Get,
            get_type=ElementGetAttributeTypeFlag.GetAttribute,
            attribute_name="src",  # 获取 src 属性
            element_timeout=10,
        )

        logger.info(f"外圈图片 src: {src_url}")

        # 第一步：下载外圈图片并转为 base64
        response = requests.get(src_url, timeout=10)
        image_bytes = response.content

        out_ring_image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        src_url = BrowserElement.element_operation(
            browser_obj=browser_obj,
            element_data=inner_circle_image_obj,  # 已拾取的 img 元素
            operation_type=ElementAttributeOpTypeFlag.Get,
            get_type=ElementGetAttributeTypeFlag.GetAttribute,
            attribute_name="src",  # 获取 src 属性
            element_timeout=10,
        )

        logger.info(f"内圈图片 src: {src_url}")

        # 第二步：下载内圈图片并转为 base64
        response = requests.get(src_url, timeout=10)
        image_bytes = response.content

        inner_circle_image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # 调用第三方API识别旋转角度（使用双圈旋转验证码类型）
        # 将两张图片合并传递给API，或者根据API要求分别传递
        rotate_angle = int(
            VerifyCodeCore.get_api_result(
                api_type="411115",
                pic_element_base64="",
                extra="",
                out_ring_image=out_ring_image_base64,
                inner_circle_image=inner_circle_image_base64,
            )
        )
        logger.info("双圈旋转验证码返回旋转角度: {}".format(rotate_angle))

        if rotate_angle is None:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 获取滑动条元素，计算可拖动距离
        slide_bar_element = Locator.locator(
            slide_bar_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value
        )
        slide_bar_rect = slide_bar_element.rect()

        # 获取滑块元素
        slider_element = Locator.locator(slider_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        if isinstance(slider_element.rect(), list):
            raise BizException(ELEMENT_NOT_UNIQUE, "滑块元素定位不唯一，请检查！")

        slider_start_pos = slider_element.point()

        # 计算滑动距离：根据旋转角度和最大旋转角度计算
        max_angle = int(max_rotate_angle.value)
        slide_bar_width = slide_bar_rect.width()
        drag_distance = int((rotate_angle / max_angle) * slide_bar_width)

        logger.info(
            "最大旋转角度: {}°, 需要旋转角度: {}°, 滑动条宽度: {}px, 计算拖动距离: {}px".format(
                max_angle, rotate_angle, slide_bar_width, drag_distance
            )
        )

        # 执行拖动操作
        end_pos = (slider_start_pos.x + drag_distance, slider_start_pos.y)
        VerifyCodeCore.html_drag_plus(slider_start_pos, end_pos)

        logger.info("双圈旋转验证码拖动完成")

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("background_img_obj", required=True),
        ],
        outputList=[],
    )
    def trajectory_slider_code(
        browser_obj: Browser = None,
        background_img_obj: WebPick = None,
    ):
        """通用轨迹验证码（滑块轨迹验证）

        Args:
            browser_obj: 浏览器对象
            background_img_obj: 背景图片对象（待识别的轨迹背景图）
        """
        # 获取背景图片元素并截图
        element = Locator.locator(background_img_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("轨迹验证码背景图rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 调用第三方API识别轨迹验证码（使用轨迹验证码类型）
        trajectory_result = VerifyCodeCore.get_api_result(
            api_type="100016",
            pic_element_base64=image_base64,
        )
        logger.info("轨迹验证码返回值: {}".format(trajectory_result))

        if not trajectory_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 解析轨迹数据并执行拖动操作
        # 假设返回格式为: "x1,y1|x2,y2|x3,y3|..." 表示轨迹点序列
        trajectory_points = []
        for point_str in trajectory_result.split("|"):
            parts = point_str.split(",")
            if len(parts) >= 2:
                trajectory_points.append((int(parts[0]), int(parts[1])))

        if not trajectory_points:
            raise BizException(API_RESULT_EMPTY, "轨迹数据解析失败")

        # 执行轨迹拖动
        logger.info("开始执行轨迹拖动，共 {} 个轨迹点".format(len(trajectory_points)))

        # 移动到起始点
        start_x = trajectory_points[0][0] + rect.left
        start_y = trajectory_points[0][1] + rect.top
        smooth_move(start_x, start_y, duration=0.3)
        pyautogui.mouseDown()
        time.sleep(0.1)

        # 按照轨迹点移动
        for i, point in enumerate(trajectory_points[1:], 1):
            abs_x = point[0] + rect.left
            abs_y = point[1] + rect.top
            smooth_move(abs_x, abs_y, duration=0.05)
            time.sleep(0.02)

        # 释放鼠标
        pyautogui.mouseUp()
        logger.info("轨迹验证码拖动完成")

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("captcha_img_obj", required=True),
            atomicMg.param(
                "need_input",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                required=True,
            ),
            atomicMg.param(
                "input_box_obj",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_box_obj.show",
                        expression="return  $this.need_input.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("calculation_result", types="Int")],
    )
    def numeric_calculation_code(
        browser_obj: Browser = None,
        captcha_img_obj: WebPick = None,
        need_input: bool = False,
        input_box_obj: WebPick = None,
    ) -> int:
        """通用数字计算验证码（数学计算题验证码）

        Args:
            browser_obj: 浏览器对象
            captcha_img_obj: 验证码图片对象（待识别的数字计算题图片）
            need_input: 是否填写输入框
            input_box_obj: 输入框对象（仅当 need_input 为"是"时必填）

        Returns:
            int: 验证码图片中数学算式的计算结果
        """
        # 获取验证码图片元素并截图
        element = Locator.locator(captcha_img_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("数字计算验证码图片rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 调用第三方API识别数字计算验证码（使用数字计算验证码类型）
        calculation_result = VerifyCodeCore.get_api_result(
            api_type="50100",
            pic_element_base64=image_base64,
        )
        logger.info("数字计算验证码返回值: {}".format(calculation_result))

        if not calculation_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 将结果转换为整数
        try:
            result_int = int(calculation_result)
        except ValueError:
            raise BizException(API_RESULT_EMPTY, "计算结果格式错误: {}".format(calculation_result))

        # 如果需要填写输入框
        if need_input:
            if not input_box_obj:
                raise BizException(PARAM_INVALID, "需要填写输入框时，输入框对象不能为空")
            BrowserElement.input(browser_obj=browser_obj, element_data=input_box_obj, fill_input=str(result_int))
            logger.info("已将计算结果 {} 填入输入框".format(result_int))

        return result_int

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param("browser_obj", required=True),
            atomicMg.param("captcha_img_obj", required=True),
            atomicMg.param(
                "need_input",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                required=True,
            ),
            atomicMg.param(
                "input_box_obj",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_box_obj.show",
                        expression="return  $this.need_input.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("calculation_result", types="Int")],
    )
    def chinese_calculation_code(
        browser_obj: Browser = None,
        captcha_img_obj: WebPick = None,
        need_input: bool = False,
        input_box_obj: WebPick = None,
    ) -> int:
        """通用中文计算验证码（中文数学计算题验证码）

        Args:
            browser_obj: 浏览器对象
            captcha_img_obj: 验证码图片对象（待识别的中文计算题图片）
            need_input: 是否填写输入框
            input_box_obj: 输入框对象（仅当 need_input 为"是"时必填）

        Returns:
            int: 中文计算题的答案
        """
        # 获取验证码图片元素并截图
        element = Locator.locator(captcha_img_obj.get("elementData"), cur_target_app=browser_obj.browser_type.value)
        rect = element.rect()
        logger.info("中文计算验证码图片rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 调用第三方API识别中文计算验证码（使用中文计算验证码类型）
        calculation_result = VerifyCodeCore.get_api_result(
            api_type="50101",
            pic_element_base64=image_base64,
        )
        logger.info("中文计算验证码返回值: {}".format(calculation_result))

        if not calculation_result:
            raise BizException(API_RESULT_EMPTY, "第三方接口返回为空")

        # 将结果转换为整数
        try:
            result_int = int(calculation_result)
        except ValueError:
            raise BizException(API_RESULT_EMPTY, "计算结果格式错误: {}".format(calculation_result))

        # 如果需要填写输入框
        if need_input:
            if not input_box_obj:
                raise BizException(PARAM_INVALID, "需要填写输入框时，输入框对象不能为空")
            BrowserElement.input(browser_obj=browser_obj, element_data=input_box_obj, fill_input=str(result_int))
            logger.info("已将计算结果 {} 填入输入框".format(result_int))

        return result_int
