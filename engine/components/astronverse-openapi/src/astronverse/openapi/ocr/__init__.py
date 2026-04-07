from astronverse.openapi.ocr.general import ocr_general
from astronverse.openapi.ocr.document import ocr_document
from astronverse.openapi.ocr.pdf import ocr_pdf
from astronverse.openapi.ocr.ticket import ocr_ticket
from astronverse.openapi.ocr.id_card import ocr_id_card
from astronverse.openapi.ocr.bank_card import ocr_bank_card
from astronverse.openapi.ocr.business_card import ocr_business_card
from astronverse.openapi.ocr.business_license import ocr_business_license
from astronverse.openapi.ocr.vat_invoice import ocr_vat_invoice


def train_ticket(
    is_multi: bool = False,
    src_file = "",
    src_dir = "",
    is_save: bool = True,
    dst_file = "",
    dst_file_name: str = "train_ticket_ocr",
) -> list:
    return ocr_ticket(
        ticket_type="train_ticket",
        is_multi=is_multi,
        src_file=src_file,
        src_dir=src_dir,
        is_save=is_save,
        dst_file=dst_file,
        dst_file_name=dst_file_name,
    )


def taxi_ticket(
    is_multi: bool = False,
    src_file = "",
    src_dir = "",
    is_save: bool = True,
    dst_file = "",
    dst_file_name: str = "taxi_ticket_ocr",
) -> list:
    return ocr_ticket(
        ticket_type="taxi_receipt",
        is_multi=is_multi,
        src_file=src_file,
        src_dir=src_dir,
        is_save=is_save,
        dst_file=dst_file,
        dst_file_name=dst_file_name,
    )


__all__ = [
    "ocr_general",
    "ocr_document",
    "ocr_pdf",
    "ocr_ticket",
    "ocr_id_card",
    "ocr_bank_card",
    "ocr_business_card",
    "ocr_business_license",
    "ocr_vat_invoice",
    "train_ticket",
    "taxi_ticket",
]
