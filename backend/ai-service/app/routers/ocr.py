import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.config import get_settings
from app.dependencies.points import PointChecker, PointsContext
from app.logger import get_logger
from app.schemas.ocr import (
    BankCardOCRResponse,
    BusinessCardOCRResponse,
    BusinessLicenseOCRResponse,
    DocumentOCRRequest,
    DocumentOCRResponse,
    IDCardOCRResponse,
    OCRGeneralDecodedResponseBody,
    OCRGeneralRequestBody,
    PDFOCRResponseBody,
    TicketOCRRequest,
    TicketOCRResponse,
    VATInvoiceOCRResponse,
)
from app.services.point import PointTransactionType
from app.utils.ocr import OCRError, recognize_text_from_image
from app.utils.ocr.bank_card_ocr import BankCardOCRClient
from app.utils.ocr.business_card_ocr import BusinessCardOCRClient
from app.utils.ocr.business_license_ocr import BusinessLicenseOCRClient
from app.utils.ocr.document_ocr import DocumentOCRClient
from app.utils.ocr.id_card_ocr import IDCardOCRClient
from app.utils.ocr.pdf_ocr import PDFOCRClient
from app.utils.ocr.ticket_ocr import TicketOCRClient
from app.utils.ocr.vat_invoice_ocr import VATInvoiceOCRClient

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ocr",
    tags=["开放平台OCR"],
)


def _wrap_specialized_ocr_result(data: dict) -> dict:
    return {
        "code": "0",
        "desc": "success",
        "data": data,
    }


async def _raise_ocr_http_error(prefix: str, error: OCRError, points_context: PointsContext | None = None) -> None:
    if points_context and error.should_deduct_points:
        await points_context.deduct_points()
        logger.info("%s failed after upstream processing, points deducted", prefix)

    raise HTTPException(status_code=error.status_code, detail=f"{prefix} failed: {error.message}")


@router.post("/general", response_model=OCRGeneralDecodedResponseBody)
async def general_ocr(
    params: OCRGeneralRequestBody,
    points_context: PointsContext = Depends(
        PointChecker(get_settings().OCR_GENERAL_POINTS_COST, PointTransactionType.XFYUN_COST),
    ),
):
    """
    Perform OCR on an image using Xunfei's general text recognition API.

    Returns:
        OCR result in the following format:
        {
          "header": {
            "code": 0,
            "message": "success",
            "sid": "ase000d1688@hu17b34308ea40210882"
          },
          "data": {
            "...": "decoded OCR result"
          }
        }

    Raises:
        HTTPException: 400 for invalid requests, 500 for server errors, 503 for network issues
    """
    try:
        # 调用上游 OCR 服务
        result = await recognize_text_from_image(params.image, params.encoding, params.status)

        # 检查结果并处理积分扣除
        if result.header.code == 0:
            # 成功时才扣除积分
            await points_context.deduct_points()
            logger.info("OCR processing successful, points deducted for user")

        return result

    except OCRError as e:
        # 业务逻辑错误 - 400 Bad Request
        logger.error(f"OCR business logic error: {e.message}")
        await _raise_ocr_http_error("OCR processing", e, points_context)

    except httpx.HTTPError as e:
        # 网络错误 - 503 Service Unavailable
        logger.error(f"OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        # 其他未预期的错误 - 500 Internal Server Error
        logger.error(f"Unexpected error in OCR processing: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during OCR processing")


@router.post("/document", response_model=DocumentOCRResponse)
async def document_ocr(
    params: DocumentOCRRequest,
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    通用文档识别（OCR大模型）.

    基于星火大模型的文档识别能力，支持公式、图表、栏目等复杂场景。

    Args:
        params: 请求参数，包含 base64 编码的图像和输出配置

    Returns:
        DocumentOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = DocumentOCRClient()
        result = await client.recognize(
            params.image, params.encoding, params.output_level, params.output_format
        )

        # 成功时扣除积分
        if result.header.code == 0:
            await points_context.deduct_points()
            logger.info("Document OCR processing successful, points deducted")

        return result

    except OCRError as e:
        logger.error(f"Document OCR business logic error: {e.message}")
        await _raise_ocr_http_error("Document OCR", e, points_context)

    except httpx.HTTPError as e:
        logger.error(f"Document OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Document OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in Document OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during Document OCR")


@router.post("/pdf", response_model=PDFOCRResponseBody)
async def pdf_ocr(
    request: Request,
    file: UploadFile = File(None),
    pdf_url: str = Form(None),
    export_format: str = Form("json"),
    points_context: PointsContext = Depends(
        PointChecker(0, PointTransactionType.XFYUN_COST),  # 初始不扣费，按页数计费
    ),
):
    """
    PDF 文档识别（OCR大模型）.

    支持多页 PDF 文档识别，按页数计费（10 积分/页）。

    Args:
        file: 上传的 PDF 文件（与 pdf_url 二选一）
        pdf_url: PDF 文件的公网 URL（与 file 二选一）
        export_format: 导出格式 (word, markdown, json)

    Returns:
        PDFOCRResponseBody: 包含 payload 的任务信息

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        if not pdf_url and "application/json" in (request.headers.get("content-type") or "").lower():
            body = await request.json()
            if isinstance(body, dict):
                pdf_url = body.get("pdf_url") or pdf_url
                export_format = body.get("export_format") or export_format

        if not file and not pdf_url:
            raise HTTPException(status_code=400, detail="Either file or pdf_url must be provided")

        client = PDFOCRClient()
        result = await client.recognize(file, pdf_url, export_format)

        # 按页数扣费：10 积分/页
        if result.status == "FINISH":
            points_to_deduct = result.page_count * 10
            await points_context.deduct_custom_points(points_to_deduct)
            logger.info(f"PDF OCR completed, {result.page_count} pages, deducted {points_to_deduct} points")

        return {"payload": result}

    except OCRError as e:
        logger.error(f"PDF OCR business logic error: {e.message}")
        await _raise_ocr_http_error("PDF OCR", e)

    except HTTPException:
        raise

    except httpx.HTTPError as e:
        logger.error(f"PDF OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="PDF OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in PDF OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during PDF OCR")


@router.post("/ticket", response_model=TicketOCRResponse)
async def ticket_ocr(
    file: UploadFile = File(...),
    ocr_type: str = Form("air_itinerary"),
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    票据卡证识别.

    支持行程单、火车票、出租车票等多种票据类型识别。

    Args:
        file: 上传的图片文件
        ocr_type: 票据类型 (air_itinerary, train_ticket, taxi_receipt等)

    Returns:
        TicketOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = TicketOCRClient()
        result = await client.recognize(file=file, ocr_type=ocr_type)

        # 成功时扣除积分
        await points_context.deduct_points()
        logger.info("Ticket OCR processing successful, points deducted")

        return {"data": result}

    except OCRError as e:
        logger.error(f"Ticket OCR business logic error: {e.message}")
        await _raise_ocr_http_error("Ticket OCR", e, points_context)

    except httpx.HTTPError as e:
        logger.error(f"Ticket OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Ticket OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in Ticket OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during Ticket OCR")


@router.post("/business-card", response_model=BusinessCardOCRResponse)
async def business_card_ocr(
    file: UploadFile = File(...),
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    名片识别.

    识别名片上的姓名、电话、邮箱、公司等信息。

    Args:
        file: 上传的图片文件

    Returns:
        BusinessCardOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = BusinessCardOCRClient()
        result = await client.recognize(file)
        logger.info(f"Business card OCR raw result: {result}")

        # 成功时扣除积分
        await points_context.deduct_points()
        logger.info("Business card OCR processing successful, points deducted")

        return _wrap_specialized_ocr_result(result)

    except OCRError as e:
        logger.error(f"Business card OCR business logic error: {e.message}")
        await _raise_ocr_http_error("Business card OCR", e, points_context)

    except httpx.HTTPError as e:
        logger.error(f"Business card OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Business card OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in Business card OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during Business card OCR")


@router.post("/id-card", response_model=IDCardOCRResponse)
async def id_card_ocr(
    file: UploadFile = File(...),
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    身份证识别.

    识别身份证正反面信息，包括姓名、身份证号、地址等。

    Args:
        file: 上传的图片文件

    Returns:
        IDCardOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = IDCardOCRClient()
        result = await client.recognize(file)

        # 成功时扣除积分
        await points_context.deduct_points()
        logger.info("ID card OCR processing successful, points deducted")

        return _wrap_specialized_ocr_result(result)

    except OCRError as e:
        logger.error(f"ID card OCR business logic error: {e.message}")
        await _raise_ocr_http_error("ID card OCR", e, points_context)

    except httpx.HTTPError as e:
        logger.error(f"ID card OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="ID card OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in ID card OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during ID card OCR")


@router.post("/bank-card", response_model=BankCardOCRResponse)
async def bank_card_ocr(
    file: UploadFile = File(...),
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    银行卡识别.

    识别银行卡号、有效期、持卡人姓名等信息。

    Args:
        file: 上传的图片文件

    Returns:
        BankCardOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = BankCardOCRClient()
        result = await client.recognize(file)

        # 成功时扣除积分
        await points_context.deduct_points()
        logger.info("Bank card OCR processing successful, points deducted")

        return _wrap_specialized_ocr_result(result)

    except OCRError as e:
        logger.error(f"Bank card OCR business logic error: {e.message}")
        await _raise_ocr_http_error("Bank card OCR", e, points_context)

    except httpx.HTTPError as e:
        logger.error(f"Bank card OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Bank card OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in Bank card OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during Bank card OCR")


@router.post("/business-license", response_model=BusinessLicenseOCRResponse)
async def business_license_ocr(
    file: UploadFile = File(...),
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    营业执照识别.

    识别营业执照上的企业名称、注册号、法定代表人等信息。

    Args:
        file: 上传的图片文件

    Returns:
        BusinessLicenseOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = BusinessLicenseOCRClient()
        result = await client.recognize(file)

        # 成功时扣除积分
        await points_context.deduct_points()
        logger.info("Business license OCR processing successful, points deducted")

        return _wrap_specialized_ocr_result(result)

    except OCRError as e:
        logger.error(f"Business license OCR business logic error: {e.message}")
        await _raise_ocr_http_error("Business license OCR", e, points_context)

    except httpx.HTTPError as e:
        logger.error(f"Business license OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Business license OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in Business license OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during Business license OCR")


@router.post("/vat-invoice", response_model=VATInvoiceOCRResponse)
async def vat_invoice_ocr(
    file: UploadFile = File(...),
    points_context: PointsContext = Depends(
        PointChecker(50, PointTransactionType.XFYUN_COST),
    ),
):
    """
    增值税发票识别.

    识别增值税发票上的发票代码、发票号码、金额等信息。

    Args:
        file: 上传的图片文件

    Returns:
        VATInvoiceOCRResponse: 识别结果

    Raises:
        HTTPException: 400/500/503 错误
    """
    try:
        client = VATInvoiceOCRClient()
        result = await client.recognize(file)

        # 成功时扣除积分
        await points_context.deduct_points()
        logger.info("VAT invoice OCR processing successful, points deducted")

        return _wrap_specialized_ocr_result(result)

    except OCRError as e:
        logger.error(f"VAT invoice OCR business logic error: {e.message}")
        await _raise_ocr_http_error("VAT invoice OCR", e, points_context)

    except httpx.HTTPError as e:
        logger.error(f"VAT invoice OCR service network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="VAT invoice OCR service is temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.error(f"Unexpected error in VAT invoice OCR: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during VAT invoice OCR")
