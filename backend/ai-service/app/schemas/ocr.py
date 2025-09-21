from typing import Optional
from pydantic import BaseModel, Field


class OCRGeneralRequestBody(BaseModel):
    encoding: str = Field(
        "jpg",
        description="图像编码，jpg格式(默认值)/jpeg格式/png格式/bmp格式",
        examples=["jpg"],
    )
    status: int = Field(
        3, description="上传数据状态，可选值：3（一次传完）", examples=[3]
    )
    image: str = Field(
        ...,
        description="图像数据，需保证图像文件大小base64编码后不超过4MB",
        examples=["iVBORw0KGgoAAAANSUhEUgAA..."],
    )


class OCRGeneralResponseInnerHeader(BaseModel):
    code: int = Field(..., description="返回码，0表示成功，非0表示失败", examples=[0])
    message: str = Field(..., description="返回信息", examples=["success"])
    sid: str = Field(
        ..., description="会话唯一标识", examples=["ase000fa8ab@hu196fbeb910905c4882"]
    )


class OCRGeneralResponseInnerResult(BaseModel):
    compress: str = Field(..., description="文本压缩格式", examples=["raw"])
    encoding: str = Field(..., description="文本编码格式", examples=["utf8"])
    format: str = Field(..., description="文本格式", examples=["json"])
    text: str = Field(
        ...,
        description="返回的文本数据， 需要对其进行base64解码",
        examples=["fQogXQp9Cg=="],
    )


class OCRGeneralResponseInnerPayload(BaseModel):
    result: OCRGeneralResponseInnerResult


class OCRGeneralResponseBody(BaseModel):
    header: OCRGeneralResponseInnerHeader
    payload: Optional[OCRGeneralResponseInnerPayload]
