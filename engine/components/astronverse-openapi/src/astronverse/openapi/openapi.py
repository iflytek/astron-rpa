from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, AtomicOption, DynamicsItem
from pathlib import Path

from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH
from astronverse.openapi.error import BizException, IMAGE_EMPTY
from astronverse.openapi.ocr import (
    ocr_bank_card as run_ocr_bank_card,
    ocr_business_card as run_ocr_business_card,
    ocr_business_license as run_ocr_business_license,
    ocr_document as run_ocr_document,
    ocr_general as run_ocr_general,
    ocr_id_card as run_ocr_id_card,
    ocr_pdf as run_ocr_pdf,
    ocr_ticket as run_ocr_ticket,
    ocr_vat_invoice as run_ocr_vat_invoice,
    taxi_ticket as run_taxi_ticket,
    train_ticket as run_train_ticket,
)
from astronverse.openapi.nlp import (
    nlp_text_correction as run_nlp_text_correction,
    nlp_text_moderation as run_nlp_text_moderation,
    nlp_translate as run_nlp_translate,
)
from astronverse.openapi.speech import (
    speech_asr_multilingual as run_speech_asr_multilingual,
    speech_asr_zh as run_speech_asr_zh,
    speech_transcribe_audio as run_speech_transcribe_audio,
    speech_tts_ultra_human as run_speech_tts_ultra_human,
)
from astronverse.openapi.speech._common import _post_speech

IMAGE_FILTERS = [".jpeg", ".jpg", ".png", ".gif", ".bmp"]
AUDIO_FILE_FILTERS = [
    ".mp3",
    ".wav",
    ".pcm",
    ".mp4",
    ".m4a",
    ".aac",
    ".opus",
    ".flac",
    ".ogg",
    ".amr",
    ".speex",
    ".lyb",
    ".ac3",
    ".ape",
    ".m4r",
    ".acc",
    ".wma",
]
LONG_TEXT_FILE_FILTERS = [".txt", ".md", ".json", ".xml"]
ULTRA_HUMAN_TEXT_FILE_FILTERS = [".txt", ".md", ".json"]
LONG_TEXT_VOICE_OPTIONS = [
    ("小果-女声-新闻播报", "xiaoguo"),
    ("超哥-男声-新闻播报", "chaoge"),
    ("聆飞皓-男声-直播广告", "lingfeihao"),
]
ULTRA_HUMAN_VOICE_OPTIONS = [
    ("聆飞博-男声-时政新闻", "lingfeibo"),
    ("Lila-美式英语-女声-交互聊天", "Lila"),
    ("Grant-美式英语-男声-交互聊天", "Grant"),
    ("聆飞逸-男声-交互聊天", "x5_lingfeiyi_flow"),
    ("聆小璇-女声-交互聊天", "x5_lingxiaoxuan_flow"),
    ("聆小玥-女声-交互聊天", "x5_lingxiaoyue_flow"),
    ("聆玉昭-女声-交互聊天", "x5_lingyuzhao_flow"),
    ("聆玉言-女声-交互聊天", "x5_lingyuyan_flow"),
]
LONG_TEXT_AUDIO_FORMAT_OPTIONS = [
    ("pcm", "pcm"),
    ("mp3", "mp3"),
    ("speex 8K", "speex_8k"),
    ("speex 16K", "speex_16k"),
    ("opus 8K", "opus_8k"),
    ("opus 16K", "opus_16k"),
]
ULTRA_HUMAN_FILE_AUDIO_FORMAT_OPTIONS = [
    ("pcm", "pcm"),
    ("mp3", "mp3"),
    ("opus 8K", "opus_8k"),
    ("opus 16K", "opus_16k"),
    ("opus 24K", "opus_24k"),
    ("speex 8K", "speex_8k"),
    ("speex 16K", "speex_16k"),
]


def _image_file_param(key: str, show_when: str | None = None):
    kwargs = {
        "formType": AtomicFormTypeMeta(
            type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
            params={"file_type": "file", "filters": IMAGE_FILTERS},
        )
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    return atomicMg.param(key, **kwargs)


def _folder_param(key: str, show_when: str | None = None):
    kwargs = {
        "formType": AtomicFormTypeMeta(
            type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
            params={"file_type": "folder"},
        )
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    return atomicMg.param(key, **kwargs)


def _file_param(key: str, filters: list[str], show_when: str | None = None):
    kwargs = {
        "types": "PATH",
        "formType": AtomicFormTypeMeta(
            type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
            params={"file_type": "file", "filters": filters},
        ),
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    return atomicMg.param(key, **kwargs)


def _select_param(key: str, values: list[str]):
    return atomicMg.param(
        key,
        types=key,
        formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
        options=[AtomicOption(value, value) for value in values],
    )


def _select_option_param(key: str, options: list[tuple[str, str]], default: str):
    return atomicMg.param(
        key,
        types=key,
        formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
        options=[AtomicOption(label, value) for label, value in options],
        default=default,
        required=True,
    )


def _switch_param(key: str, default: bool, show_when: str | None = None):
    kwargs = {
        "types": "Bool",
        "formType": AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
        "default": default,
        "required": True,
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    return atomicMg.param(key, **kwargs)


def _text_param(key: str):
    return atomicMg.param(key, types="Str")


def _textarea_param(key: str, show_when: str | None = None, limit_length: int | None = None):
    kwargs = {
        "types": "Str",
        "formType": AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    if limit_length is not None:
        kwargs["limitLength"] = [-1, limit_length]
    return atomicMg.param(key, **kwargs)


def _integer_param(key: str, default: int, show_when: str | None = None):
    kwargs = {
        "types": "Int",
        "formType": AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
        "default": default,
        "required": True,
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    return atomicMg.param(key, **kwargs)


def _radio_param(key: str, options: list[tuple[str, str]], default: str):
    return atomicMg.param(
        key,
        types=key,
        formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
        options=[AtomicOption(label, value) for label, value in options],
        default=default,
        required=True,
    )


def _multi_select_param(key: str, options: list[tuple[str, str]], default: list[str]):
    return atomicMg.param(
        key,
        types="List",
        formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"multiple": True}),
        options=[AtomicOption(label, value) for label, value in options],
        default=default,
        required=True,
    )


def _ocr_image_inputs():
    return [
        _image_file_param("src_file", "return $this.is_multi.value == false"),
        _folder_param("src_dir", "return $this.is_multi.value == true"),
        _folder_param("dst_file", "return $this.is_save.value == true"),
    ]


def _raise_validation(message: str) -> None:
    raise BizException(IMAGE_EMPTY, message)


def _resolve_text_input(
    *,
    input_type: str,
    text: str,
    src_file: str,
    filters: list[str],
    file_empty_message: str,
    text_empty_message: str,
    oversize_message: str,
    max_chars: int | None = None,
    max_bytes: int | None = None,
    max_file_bytes: int | None = None,
) -> str:
    if input_type == "file":
        if not src_file:
            _raise_validation(file_empty_message)
        files = utils.generate_src_files(src_file, file_type="file")
        if not files:
            _raise_validation(file_empty_message)
        file_path = files[0]
        if Path(file_path).suffix.lower() not in filters:
            _raise_validation(file_empty_message)
        if max_file_bytes is not None and Path(file_path).stat().st_size > max_file_bytes:
            _raise_validation(oversize_message)
        text = Path(file_path).read_text(encoding="utf-8")
    elif not text:
        _raise_validation(text_empty_message)

    if max_chars is not None and len(text) > max_chars:
        _raise_validation(oversize_message)
    if max_bytes is not None and len(text.encode("utf-8")) > max_bytes:
        _raise_validation(oversize_message)
    return text


def _ensure_supported_tts_format(audio_format: str) -> None:
    if audio_format not in {"mp3", "pcm"}:
        _raise_validation(f"当前 backend 暂不支持 {audio_format} 输出格式")


class OpenApi:
    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("id_card", types="List")])
    def id_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "id_card_ocr",
    ) -> list:
        return run_ocr_id_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("business_license", types="List")],
    )
    def business_license(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "business_license_ocr",
    ) -> list:
        return run_ocr_business_license(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("vat_invoice", types="List")])
    def vat_invoice(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "vat_invoice_ocr",
    ) -> list:
        return run_ocr_vat_invoice(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("train_ticket", types="List")],
    )
    def train_ticket(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "train_ticket_ocr",
    ) -> list:
        return run_train_ticket(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("taxi_ticket", types="List")],
    )
    def taxi_ticket(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "taxi_ticket_ocr",
    ) -> list:
        return run_taxi_ticket(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("common_ocr", types="List")])
    def common_ocr(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "common_ocr",
    ) -> list:
        return run_ocr_general(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("ocr_general", types="List")])
    def ocr_general(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "general_ocr",
    ) -> list:
        return run_ocr_general(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _image_file_param("src_file"),
            _select_param("output_format", ["markdown", "json"]),
            _folder_param("dst_file", "return $this.is_save.value == true"),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("raw", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def ocr_document(
        src_file: PATH = "",
        output_format: str = "markdown",
        output_level: int = 1,
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "document_ocr",
    ) -> dict:
        return run_ocr_document(
            src_file=src_file,
            output_format=output_format,
            output_level=output_level,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("URL外链", "url")], "file"),
            atomicMg.param(
                "is_multi",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=False,
                dynamics=[DynamicsItem(key="$this.is_multi.show", expression="return $this.input_type.value == 'file'")],
                required=True,
            ),
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file", "filters": [".pdf"]},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == false",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "src_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == true",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "pdf_url",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[DynamicsItem(key="$this.pdf_url.show", expression="return $this.input_type.value == 'url'")],
                required=True,
            ),
            atomicMg.param(
                "page_mode",
                types="page_mode",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                options=[AtomicOption("全部页面", "all"), AtomicOption("自定义页码", "custom")],
                default="all",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_mode.show",
                        expression="return $this.input_type.value == 'url' || $this.is_multi.value == false",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "page_ranges",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[DynamicsItem(key="$this.page_ranges.show", expression="return $this.page_mode.value == 'custom'")],
                required=True,
            ),
            atomicMg.param(
                "export_format",
                types="export_format",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                options=[
                    AtomicOption("word", "word"),
                    AtomicOption("json", "json"),
                    AtomicOption("markdown", "markdown"),
                ],
                default="word",
                required=True,
            ),
            atomicMg.param(
                "dst_file",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                required=True,
            ),
            atomicMg.param(
                "dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="pdf_ocr",
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("task_no", types="Str"),
            atomicMg.param("status", types="Str"),
            atomicMg.param("page_count", types="Int"),
            atomicMg.param("result_url", types="Str"),
        ],
    )
    def ocr_pdf(
        input_type: str = "file",
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        pdf_url: str = "",
        page_mode: str = "all",
        page_ranges: str = "",
        export_format: str = "json",
        dst_file: PATH = "",
        dst_file_name: str = "pdf_ocr",
    ) -> dict:
        return run_ocr_pdf(
            src_file=src_file,
            pdf_url=pdf_url,
            export_format=export_format,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[_select_param("ticket_type", ["train_ticket", "taxi_receipt", "air_itinerary"]), *_ocr_image_inputs()],
        outputList=[atomicMg.param("ocr_ticket", types="List")],
    )
    def ocr_ticket(
        ticket_type: str = "train_ticket",
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "ticket_ocr",
    ) -> list:
        return run_ocr_ticket(
            ticket_type=ticket_type,
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("ocr_id_card", types="List")])
    def ocr_id_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "id_card_ocr",
    ) -> list:
        return run_ocr_id_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_bank_card", types="List")],
    )
    def ocr_bank_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "bank_card_ocr",
    ) -> list:
        return run_ocr_bank_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_business_card", types="List")],
    )
    def ocr_business_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "business_card_ocr",
    ) -> list:
        return run_ocr_business_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_business_license", types="List")],
    )
    def ocr_business_license(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "business_license_ocr",
    ) -> list:
        return run_ocr_business_license(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_vat_invoice", types="List")],
    )
    def ocr_vat_invoice(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "vat_invoice_ocr",
    ) -> list:
        return run_ocr_vat_invoice(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("URL形式", "url")], "file"),
            _file_param("src_file", AUDIO_FILE_FILTERS, "return $this.input_type.value == 'file'"),
            atomicMg.param(
                "audio_url",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[DynamicsItem(key="$this.audio_url.show", expression="return $this.input_type.value == 'url'")],
                required=True,
            ),
            _switch_param("role_type", False),
            _integer_param("role_num", 0, "return $this.role_type.value == true"),
            _switch_param("is_save", True),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            atomicMg.param(
                "dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="audio_transcription",
                dynamics=[DynamicsItem(key="$this.dst_file_name.show", expression="return $this.is_save.value == true")],
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("result", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def speech_asr_zh(
        src_file: PATH = "",
        is_save: bool = False,
        dst_file: PATH = "",
        dst_file_name: str = "speech_asr_zh",
        save_format: str = "txt",
    ) -> dict:
        return run_speech_asr_zh(
            src_file=src_file,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            save_format=save_format,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            _select_param("save_format", ["txt", "json"]),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("result", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def speech_asr_multilingual(
        src_file: PATH = "",
        language: str = "en",
        is_save: bool = False,
        dst_file: PATH = "",
        dst_file_name: str = "speech_asr_multilingual",
        save_format: str = "txt",
    ) -> dict:
        return run_speech_asr_multilingual(
            src_file=src_file,
            language=language,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            save_format=save_format,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("URL形式", "url")], "file"),
            _file_param("src_file", AUDIO_FILE_FILTERS, "return $this.input_type.value == 'file'"),
            atomicMg.param(
                "audio_url",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[DynamicsItem(key="$this.audio_url.show", expression="return $this.input_type.value == 'url'")],
                required=True,
            ),
            _switch_param("role_type", False),
            _integer_param("role_num", 0, "return $this.role_type.value == true"),
            _switch_param("is_save", True),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            atomicMg.param(
                "dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="audio_transcription",
                dynamics=[DynamicsItem(key="$this.dst_file_name.show", expression="return $this.is_save.value == true")],
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("result", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def speech_transcribe_audio(
        input_type: str = "file",
        src_file: PATH = "",
        audio_url: str = "",
        language: str = "cn",
        role_type: bool = False,
        role_num: int = 0,
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "audio_transcription",
    ) -> dict:
        if input_type == "url":
            if not audio_url:
                _raise_validation("URL外链是必填的")
            _raise_validation("当前 backend 暂未支持 URL 外链转写")
        if not src_file:
            _raise_validation("文件路径是必填的")
        if role_num < 0 or role_num > 10:
            _raise_validation("请输入0-10间整数")
        return run_speech_transcribe_audio(
            src_file=src_file,
            language=language,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            save_format="txt",
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("文本形式", "text")], "text"),
            _file_param("src_file", LONG_TEXT_FILE_FILTERS, "return $this.input_type.value == 'file'"),
            _textarea_param("text", "return $this.input_type.value == 'text'", 100000),
            _select_option_param("voice", LONG_TEXT_VOICE_OPTIONS, "xiaoguo"),
            _integer_param("speed", 50),
            _integer_param("volume", 50),
            _integer_param("pitch", 50),
            _folder_param("dst_file"),
            atomicMg.param(
                "dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="long_text_speech_synthesis",
                required=True,
            ),
            _select_option_param("audio_format", LONG_TEXT_AUDIO_FORMAT_OPTIONS, "mp3"),
        ],
        outputList=[
            atomicMg.param("audio_file", types="PATH"),
            atomicMg.param("result", types="Dict"),
        ],
    )
    def speech_tts_long_text(
        input_type: str = "text",
        src_file: PATH = "",
        text: str = "",
        voice: str = "xiaoguo",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50,
        dst_file: PATH = "",
        dst_file_name: str = "long_text_speech_synthesis",
        audio_format: str = "mp3",
    ) -> dict:
        if speed < 0 or speed > 100 or volume < 0 or volume > 100 or pitch < 0 or pitch > 100:
            _raise_validation("请输入0-100间整数")
        _ensure_supported_tts_format(audio_format)
        resolved_text = _resolve_text_input(
            input_type=input_type,
            text=text,
            src_file=src_file,
            filters=LONG_TEXT_FILE_FILTERS,
            file_empty_message="文件路径是必填的",
            text_empty_message="文本内容是必填的",
            oversize_message="文本内容超出最大限制100000字符",
            max_chars=100000,
            max_bytes=1024 * 1024,
            max_file_bytes=350 * 1024,
        )
        return run_speech_tts_ultra_human(
            text=resolved_text,
            voice=voice,
            speed=speed,
            volume=volume,
            pitch=pitch,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            audio_format=audio_format,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("文本形式", "text")], "text"),
            _file_param("src_file", ULTRA_HUMAN_TEXT_FILE_FILTERS, "return $this.input_type.value == 'file'"),
            atomicMg.param(
                "text",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[DynamicsItem(key="$this.text.show", expression="return $this.input_type.value == 'text'")],
                required=True,
            ),
            _select_option_param("voice", ULTRA_HUMAN_VOICE_OPTIONS, "x5_lingyuyan_flow"),
            _integer_param("speed", 50),
            _integer_param("volume", 50),
            _integer_param("pitch", 50),
        ],
        outputList=[
            atomicMg.param("audio_base64", types="Str"),
            atomicMg.param("result", types="Dict"),
        ],
    )
    def speech_tts_ultra_human_realtime(
        input_type: str = "text",
        src_file: PATH = "",
        text: str = "",
        voice: str = "x5_lingyuyan_flow",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50,
    ) -> dict:
        if speed < 0 or speed > 100 or volume < 0 or volume > 100 or pitch < 0 or pitch > 100:
            _raise_validation("请输入0-100间整数")
        resolved_text = _resolve_text_input(
            input_type=input_type,
            text=text,
            src_file=src_file,
            filters=ULTRA_HUMAN_TEXT_FILE_FILTERS,
            file_empty_message="文件路径是必填的",
            text_empty_message="文本内容是必填的",
            oversize_message="文本内容超出最大限制64K",
            max_bytes=64 * 1024,
            max_file_bytes=64 * 1024,
        )
        response = _post_speech(
            "/speech/tts",
            {
                "text": resolved_text,
                "voice": voice,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "audio_format": "mp3",
                "sample_rate": 16000,
            },
        )
        return {"audio_base64": response["audio_base64"], "result": response["result"]}

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "input_type",
                types="input_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
                options=[AtomicOption("文件形式", "file"), AtomicOption("文本形式", "text")],
                default="text",
                required=True,
            ),
            atomicMg.param(
                "is_multi",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=False,
                dynamics=[DynamicsItem(key="$this.is_multi.show", expression="return $this.input_type.value == 'file'")],
                required=True,
            ),
            atomicMg.param(
                "src_file",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file", "filters": [".txt", ".md", ".json", ".xml"]},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == false",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "src_dir",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == true",
                    )
                ],
                required=True,
            ),
            _textarea_param("text", "return $this.input_type.value == 'text'", 2000),
            atomicMg.param(
                "is_save",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=True,
                required=True,
            ),
            atomicMg.param(
                "error_dst_file",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.error_dst_file.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "error_dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="text_correction",
                dynamics=[
                    DynamicsItem(
                        key="$this.error_dst_file_name.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "export_corrected_doc",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=False,
                required=True,
            ),
            atomicMg.param(
                "corrected_dst_file",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.corrected_dst_file.show",
                        expression="return $this.export_corrected_doc.value == true",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "corrected_dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="text_correction_corrected",
                dynamics=[
                    DynamicsItem(
                        key="$this.corrected_dst_file_name.show",
                        expression="return $this.export_corrected_doc.value == true",
                    )
                ],
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("data", types="Dict"),
            atomicMg.param("error_detail_file", types="Any"),
            atomicMg.param("corrected_file", types="Any"),
        ],
    )
    def nlp_text_correction(
        input_type: str = "text",
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        text: str = "",
        is_save: bool = True,
        error_dst_file: PATH = "",
        error_dst_file_name: str = "text_correction",
        export_corrected_doc: bool = False,
        corrected_dst_file: PATH = "",
        corrected_dst_file_name: str = "text_correction_corrected",
    ) -> dict:
        result = run_nlp_text_correction(
            input_type=input_type,
            is_multi=is_multi,
            text=text,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            error_dst_file=error_dst_file,
            error_dst_file_name=error_dst_file_name,
            export_corrected_doc=export_corrected_doc,
            corrected_dst_file=corrected_dst_file,
            corrected_dst_file_name=corrected_dst_file_name,
        )
        if isinstance(result, dict):
            return (
                result.get("data"),
                result.get("error_detail_file"),
                result.get("corrected_file"),
            )
        return result

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("文本形式", "text")], "text"),
            atomicMg.param(
                "is_multi",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=False,
                dynamics=[DynamicsItem(key="$this.is_multi.show", expression="return $this.input_type.value == 'file'")],
                required=True,
            ),
            atomicMg.param(
                "src_file",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file", "filters": [".txt", ".md", ".json", ".xml"]},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "src_dir",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == true",
                    )
                ],
                required=True,
            ),
            _textarea_param("content", "return $this.input_type.value == 'text'", 5000),
            _multi_select_param(
                "categories",
                [
                    ("色情", "pornDetection"),
                    ("暴恐", "violentTerrorism"),
                    ("涉政", "political"),
                    ("低质量灌水", "lowQualityIrrigation"),
                    ("违禁", "contraband"),
                    ("广告", "advertisement"),
                    ("不文明用语", "uncivilizedLanguage"),
                ],
                [
                    "pornDetection",
                    "violentTerrorism",
                    "political",
                    "lowQualityIrrigation",
                    "contraband",
                    "advertisement",
                    "uncivilizedLanguage",
                ],
            ),
            atomicMg.param(
                "is_save",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=True,
                required=True,
            ),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            atomicMg.param(
                "dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="text_moderation",
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file_name.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("data", types="Dict"),
            atomicMg.param("saved_file", types="Any"),
        ],
    )
    def nlp_text_moderation(
        input_type: str = "text",
        is_multi: bool = False,
        content: str = "",
        src_file: PATH = "",
        src_dir: PATH = "",
        categories: list = None,
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "text_moderation",
    ) -> dict:
        return run_nlp_text_moderation(
            input_type=input_type,
            is_multi=is_multi,
            content=content,
            src_file=src_file,
            src_dir=src_dir,
            categories=categories,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("文本形式", "text")], "text"),
            atomicMg.param(
                "is_multi",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=False,
                dynamics=[DynamicsItem(key="$this.is_multi.show", expression="return $this.input_type.value == 'file'")],
                required=True,
            ),
            atomicMg.param(
                "src_file",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file", "filters": [".txt", ".md", ".json", ".xml"]},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == false",
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "src_dir",
                types="PATH",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.input_type.value == 'file' && $this.is_multi.value == true",
                    )
                ],
                required=True,
            ),
            _textarea_param("text", "return $this.input_type.value == 'text'", 5000),
            _select_option_param(
                "from_lang",
                [
                    ("auto", "auto"),
                    ("中文（简体）", "cn"),
                    ("中文（繁体）", "cht"),
                    ("英语", "en"),
                    ("日语", "ja"),
                    ("韩语", "ko"),
                    ("俄语", "ru"),
                    ("法语", "fr"),
                    ("西班牙语", "es"),
                    ("阿拉伯语", "ar"),
                    ("葡萄牙语", "pt"),
                    ("德语", "de"),
                    ("印尼语", "id"),
                    ("意大利语", "it"),
                    ("荷兰语", "nl"),
                    ("泰语", "th"),
                    ("藏语", "bo"),
                    ("土耳其语", "tr"),
                ],
                "auto",
            ),
            _select_option_param(
                "to_lang",
                [
                    ("中文（简体）", "cn"),
                    ("中文（繁体）", "cht"),
                    ("英语", "en"),
                    ("日语", "ja"),
                    ("韩语", "ko"),
                    ("俄语", "ru"),
                    ("法语", "fr"),
                    ("西班牙语", "es"),
                    ("阿拉伯语", "ar"),
                    ("葡萄牙语", "pt"),
                    ("德语", "de"),
                    ("印尼语", "id"),
                    ("意大利语", "it"),
                    ("荷兰语", "nl"),
                    ("泰语", "th"),
                    ("藏语", "bo"),
                    ("土耳其语", "tr"),
                ],
                "en",
            ),
            atomicMg.param(
                "is_save",
                types="Bool",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={}),
                default=True,
                required=True,
            ),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            atomicMg.param(
                "dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="text_translation",
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file_name.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("data", types="Dict"),
            atomicMg.param("saved_file", types="Any"),
        ],
    )
    def nlp_translate(
        input_type: str = "text",
        is_multi: bool = False,
        text: str = "",
        src_file: PATH = "",
        src_dir: PATH = "",
        from_lang: str = "auto",
        to_lang: str = "en",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "text_translation",
    ) -> dict:
        return run_nlp_translate(
            input_type=input_type,
            is_multi=is_multi,
            text=text,
            src_file=src_file,
            src_dir=src_dir,
            from_lang=from_lang,
            to_lang=to_lang,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _radio_param("input_type", [("文件形式", "file"), ("文本形式", "text")], "text"),
            _file_param("src_file", ULTRA_HUMAN_TEXT_FILE_FILTERS, "return $this.input_type.value == 'file'"),
            atomicMg.param(
                "text",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[DynamicsItem(key="$this.text.show", expression="return $this.input_type.value == 'text'")],
                required=True,
            ),
            _select_option_param("voice", ULTRA_HUMAN_VOICE_OPTIONS, "x5_lingyuyan_flow"),
            _integer_param("speed", 50),
            _integer_param("volume", 50),
            _integer_param("pitch", 50),
            _folder_param("dst_file"),
            atomicMg.param(
                "dst_file_name",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                default="ultra_human_voice_file",
                required=True,
            ),
            _select_option_param("audio_format", ULTRA_HUMAN_FILE_AUDIO_FORMAT_OPTIONS, "mp3"),
        ],
        outputList=[
            atomicMg.param("audio_file", types="PATH"),
            atomicMg.param("result", types="Dict"),
        ],
    )
    def speech_tts_ultra_human(
        input_type: str = "text",
        src_file: PATH = "",
        text: str = "",
        voice: str = "x5_lingyuyan_flow",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50,
        dst_file: PATH = "",
        dst_file_name: str = "ultra_human_voice_file",
        audio_format: str = "mp3",
    ) -> dict:
        if speed < 0 or speed > 100 or volume < 0 or volume > 100 or pitch < 0 or pitch > 100:
            _raise_validation("请输入0-100间整数")
        _ensure_supported_tts_format(audio_format)
        resolved_text = _resolve_text_input(
            input_type=input_type,
            text=text,
            src_file=src_file,
            filters=ULTRA_HUMAN_TEXT_FILE_FILTERS,
            file_empty_message="文件路径是必填的",
            text_empty_message="文本内容是必填的",
            oversize_message="文本内容超出最大限制64K",
            max_bytes=64 * 1024,
            max_file_bytes=64 * 1024,
        )
        return run_speech_tts_ultra_human(
            text=resolved_text,
            voice=voice,
            speed=speed,
            volume=volume,
            pitch=pitch,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            audio_format=audio_format,
        )
