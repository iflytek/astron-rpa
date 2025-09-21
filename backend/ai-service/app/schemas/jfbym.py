from pydantic import BaseModel, Field


class JFBYMGeneralRequestBody(BaseModel):
    image: str = Field(
        ...,
        description="需要识别图片的base64字符串",
        examples=["iVBORw0KGgoAAAANSUhEUgAA..."],
    )
    type: str = Field(..., description="验证码类型", examples=["..."])


class JFBYMGeneralResponseInnerData(BaseModel):
    code: int
    data: str
    time: float
    unique_code: str


class JFBYMGeneralResponseBody(BaseModel):
    code: int = Field(
        ...,
        description="状态值，10000表示成功，其他表示失败",
        examples=[10000],
    )
    msg: str = Field(
        ...,
        description="请求说明",
        examples=["识别成功"],
    )
    data: JFBYMGeneralResponseInnerData = Field(
        None,
        description="打码数据",
        examples=[
            {
                "code": 0,
                "data": "5298",
                "time": 0.03829169273376465,
                "unique_code": "56a74a3b9b9b796b3ec554832c1cccbb",
            },
        ],
    )
