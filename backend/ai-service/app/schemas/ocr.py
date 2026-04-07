from typing import Optional

from pydantic import BaseModel, Field


class OCRGeneralRequestBody(BaseModel):
    encoding: str = Field("jpg", description="Image encoding format", examples=["jpg"])
    status: int = Field(3, description="OCR status mode", examples=[3])
    image: str = Field(..., description="Base64 encoded image", examples=["iVBORw0KGgoAAAANSUhEUgAA..."])


class OCRGeneralResponseInnerHeader(BaseModel):
    code: int = Field(..., description="Response code, 0 means success", examples=[0])
    message: str = Field(..., description="Response message", examples=["success"])
    sid: str = Field(..., description="Service request ID", examples=["ase000fa8ab@hu196fbeb910905c4882"])


class OCRGeneralResponseInnerResult(BaseModel):
    compress: str = Field(..., description="Compression mode", examples=["raw"])
    encoding: str = Field(..., description="Result encoding", examples=["utf8"])
    format: str = Field(..., description="Result format", examples=["json"])
    text: str = Field(..., description="Base64 encoded OCR payload", examples=["fQogXQp9Cg=="])


class OCRGeneralResponseInnerPayload(BaseModel):
    result: OCRGeneralResponseInnerResult


class OCRGeneralResponseBody(BaseModel):
    header: OCRGeneralResponseInnerHeader
    payload: Optional[OCRGeneralResponseInnerPayload]


class OCRGeneralDecodedResponseBody(BaseModel):
    header: OCRGeneralResponseInnerHeader
    data: dict = Field(..., description="Decoded OCR result payload", examples=[{}])


class DocumentOCRRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image", examples=["iVBORw0KGgoAAAANSUhEUgAA..."])
    encoding: str = Field("jpg", description="Image encoding format", examples=["jpg"])
    output_level: int = Field(1, description="OCR output level", examples=[1])
    output_format: str = Field("markdown", description="OCR output format", examples=["markdown"])


class DocumentOCRResponseHeader(BaseModel):
    code: int = Field(..., description="Response code, 0 means success", examples=[0])
    message: str = Field(..., description="Response message", examples=["success"])
    sid: str = Field(..., description="Service request ID", examples=["ase000fa8ab@hu196fbeb910905c4882"])


class DocumentOCRResponseResult(BaseModel):
    compress: str = Field(..., description="Compression mode", examples=["raw"])
    encoding: str = Field(..., description="Result encoding", examples=["utf8"])
    format: str = Field(..., description="Result format", examples=["json"])
    text: str = Field(..., description="Base64 encoded OCR payload", examples=["fQogXQp9Cg=="])


class DocumentOCRResponsePayload(BaseModel):
    result: DocumentOCRResponseResult


class DocumentOCRResponse(BaseModel):
    header: DocumentOCRResponseHeader
    payload: Optional[DocumentOCRResponsePayload] = None


class PDFOCRResponsePayload(BaseModel):
    task_no: str = Field(..., description="OCR task ID", examples=["task_123456"])
    status: str = Field(..., description="Task status", examples=["completed"])
    page_count: int = Field(..., description="PDF page count", examples=[10])
    result_url: Optional[str] = Field(None, description="Result file URL", examples=["https://example.com/result.json"])


class PDFOCRResponseBody(BaseModel):
    payload: PDFOCRResponsePayload


class TicketOCRRequest(BaseModel):
    ocr_type: str = Field(
        "air_itinerary",
        description="Ticket OCR type",
        examples=["air_itinerary"],
    )


class TicketOCRResponse(BaseModel):
    data: dict = Field(..., description="Ticket OCR result payload", examples=[{}])


class BusinessCardOCRResponse(BaseModel):
    code: str = Field(..., description="Response code, 0 means success", examples=["0"])
    desc: str = Field(..., description="Response description", examples=["success"])
    data: dict = Field(..., description="Business card OCR result payload", examples=[{}])
    sid: Optional[str] = Field(None, description="Service request ID", examples=["abc123"])


class IDCardOCRResponse(BaseModel):
    code: str = Field(..., description="Response code, 0 means success", examples=["0"])
    desc: str = Field(..., description="Response description", examples=["success"])
    data: dict = Field(..., description="ID card OCR result payload", examples=[{}])
    sid: Optional[str] = Field(None, description="Service request ID", examples=["abc123"])


class BankCardOCRResponse(BaseModel):
    code: str = Field(..., description="Response code, 0 means success", examples=["0"])
    desc: str = Field(..., description="Response description", examples=["success"])
    data: dict = Field(..., description="Bank card OCR result payload", examples=[{}])
    sid: Optional[str] = Field(None, description="Service request ID", examples=["abc123"])


class BusinessLicenseOCRResponse(BaseModel):
    code: str = Field(..., description="Response code, 0 means success", examples=["0"])
    desc: str = Field(..., description="Response description", examples=["success"])
    data: dict = Field(..., description="Business license OCR result payload", examples=[{}])
    sid: Optional[str] = Field(None, description="Service request ID", examples=["abc123"])


class VATInvoiceOCRResponse(BaseModel):
    code: str = Field(..., description="Response code, 0 means success", examples=["0"])
    desc: str = Field(..., description="Response description", examples=["success"])
    data: dict = Field(..., description="VAT invoice OCR result payload", examples=[{}])
    sid: Optional[str] = Field(None, description="Service request ID", examples=["abc123"])
