"""OCR utilities package for XunFei OCR services."""

from app.utils.ocr.bank_card_ocr import BankCardOCRClient
from app.utils.ocr.base import OCRError
from app.utils.ocr.business_card_ocr import BusinessCardOCRClient
from app.utils.ocr.business_license_ocr import BusinessLicenseOCRClient
from app.utils.ocr.document_ocr import DocumentOCRClient
from app.utils.ocr.error_policy import OCRFailureCategory, OCRFailureDecision, classify_ocr_failure
from app.utils.ocr.general_ocr import recognize_text_from_image
from app.utils.ocr.id_card_ocr import IDCardOCRClient
from app.utils.ocr.pdf_ocr import PDFOCRClient
from app.utils.ocr.ticket_ocr import TicketOCRClient
from app.utils.ocr.vat_invoice_ocr import VATInvoiceOCRClient

__all__ = [
    "BankCardOCRClient",
    "BusinessCardOCRClient",
    "BusinessLicenseOCRClient",
    "DocumentOCRClient",
    "IDCardOCRClient",
    "OCRError",
    "OCRFailureCategory",
    "OCRFailureDecision",
    "PDFOCRClient",
    "TicketOCRClient",
    "VATInvoiceOCRClient",
    "classify_ocr_failure",
    "recognize_text_from_image",
]
