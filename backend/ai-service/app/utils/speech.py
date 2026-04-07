import asyncio
import base64
import hashlib
import hmac
import json
import random
import string
import time
from datetime import datetime
from io import BytesIO
from time import mktime
from urllib.parse import quote, urlencode
import wave
from wsgiref.handlers import format_date_time

import httpx
import websockets
from mutagen import File as MutagenFile

from app.config import get_settings


class SpeechError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


SHORT_IAT_CHINESE_URL = "wss://iat.xf-yun.com/v1"
SHORT_IAT_MULTILINGUAL_URL = "wss://iat.cn-huabei-1.xf-yun.com/v1"
SHORT_IAT_FRAME_SIZE = 1280
SHORT_IAT_FRAME_INTERVAL_SECONDS = 0.04
SHORT_IAT_SUPPORTED_SAMPLE_RATES = {8000, 16000}


def decode_audio_base64(audio_base64: str) -> bytes:
    try:
        return base64.b64decode(audio_base64)
    except Exception as exc:
        raise SpeechError("Invalid audio_base64 payload.") from exc


def get_audio_duration_seconds(audio_bytes: bytes, filename: str) -> float:
    audio = MutagenFile(BytesIO(audio_bytes), filename=filename)
    duration = getattr(getattr(audio, "info", None), "length", None)
    if duration is None or duration <= 0:
        raise SpeechError("Unable to determine audio duration.")
    return float(duration)


def get_audio_sample_rate(audio_bytes: bytes, filename: str, fallback: int = 16000) -> int:
    audio = MutagenFile(BytesIO(audio_bytes), filename=filename)
    sample_rate = getattr(getattr(audio, "info", None), "sample_rate", None)
    if sample_rate is None or int(sample_rate) <= 0:
        return fallback
    return int(sample_rate)


def validate_short_audio_sample_rate(sample_rate: int, filename: str) -> int:
    if sample_rate not in SHORT_IAT_SUPPORTED_SAMPLE_RATES:
        raise SpeechError(
            f"Short audio ASR only supports 8000Hz or 16000Hz audio, but got {sample_rate}Hz for {filename}. "
            "Please convert the audio sample rate and try again."
        )
    return sample_rate


def normalize_short_iat_error_message(message: str) -> str:
    lowered = (message or "").strip().lower()
    if "licc fail" in lowered:
        return (
            "XFYun short ASR authorization failed for the current AppID. "
            "Please confirm the AppID/APIKey/APISecret match and that the AppID has the speech dictation service enabled."
        )
    return message


def prepare_short_audio_payload(audio_bytes: bytes, filename: str) -> tuple[bytes, str, int]:
    # 短音频识别适用于日常说话场景，通常是 60 秒以内的语音。
    # 长时间录音文件应走 transcription / IFASR LLM，而不是短音频 websocket 识别。
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix == "wav":
        try:
            with wave.open(BytesIO(audio_bytes), "rb") as wav_file:
                if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2:
                    raise SpeechError("Short audio ASR requires mono 16-bit WAV audio.")
                sample_rate = validate_short_audio_sample_rate(int(wav_file.getframerate()), filename)
                return wav_file.readframes(wav_file.getnframes()), "raw", sample_rate
        except SpeechError:
            raise
        except Exception as exc:
            raise SpeechError("Unable to parse WAV audio.") from exc
    if suffix == "mp3":
        sample_rate = validate_short_audio_sample_rate(get_audio_sample_rate(audio_bytes, filename), filename)
        return audio_bytes, "lame", sample_rate
    if suffix == "pcm":
        return audio_bytes, "raw", 16000
    raise SpeechError("Short audio ASR currently supports wav/mp3/pcm files only.")


def build_short_iat_request(
    language: str,
    audio_encoding: str,
    sample_rate: int,
    audio_chunk_base64: str,
    status: int,
    seq: int,
    *,
    include_parameters: bool,
) -> dict:
    settings = get_settings()
    if language == "zh_cn":
        iat_params = {
            "domain": "slm",
            "language": "zh_cn",
            "accent": "mandarin",
            "eos": 6000,
            "vinfo": 1,
            "result": {"encoding": "utf8", "compress": "raw", "format": "json"},
        }
    else:
        iat_params = {
            "domain": "slm",
            "language": "mul_cn",
            "accent": "mandarin",
            "eos": 6000,
            "vinfo": 1,
            "result": {"encoding": "utf8", "compress": "raw", "format": "json"},
        }
        if language not in {"", "none", "auto", "mul_cn"}:
            iat_params["ln"] = language

    header = {
        "app_id": settings.XFYUN_APP_ID,
        "status": status,
    }

    request_body = {
        "header": header,
        "payload": {
            "audio": {
                "encoding": audio_encoding,
                "sample_rate": sample_rate,
                "channels": 1,
                "bit_depth": 16,
                "seq": seq,
                "status": status,
                "audio": audio_chunk_base64,
            }
        },
    }
    if include_parameters:
        # 官方短语音 websocket 文档要求公共参数和业务参数仅在首帧传递。
        request_body["parameter"] = {"iat": iat_params}
    return request_body


def parse_short_iat_payload(result_text_base64: str) -> tuple[int, str, dict]:
    decoded = base64.b64decode(result_text_base64).decode("utf-8")
    parsed = json.loads(decoded)
    words = []
    for item in parsed.get("ws", []):
        for candidate in item.get("cw", []):
            word = candidate.get("w", "")
            if word:
                words.append(word)
                break
    return int(parsed.get("sn", 0)), "".join(words), parsed


async def recognize_short_iat(audio_bytes: bytes, filename: str, language: str) -> tuple[str, list[dict], dict]:
    stream_bytes, audio_encoding, sample_rate = prepare_short_audio_payload(audio_bytes, filename)
    settings = get_settings()
    endpoint = SHORT_IAT_CHINESE_URL if language == "zh_cn" else SHORT_IAT_MULTILINGUAL_URL
    url = assemble_ws_auth_url(endpoint, settings.XFYUN_API_KEY, settings.XFYUN_API_SECRET)

    content_map: dict[int, str] = {}
    raw_results: list[dict] = []
    segments: list[dict] = []

    async def _send_audio_frames(websocket) -> None:
        seq = 0
        status = 0
        offset = 0
        total_size = len(stream_bytes)

        while offset < total_size:
            chunk = stream_bytes[offset : offset + SHORT_IAT_FRAME_SIZE]
            offset += SHORT_IAT_FRAME_SIZE
            is_last_frame = offset >= total_size
            status = 2 if is_last_frame else status
            request = build_short_iat_request(
                language=language,
                audio_encoding=audio_encoding,
                sample_rate=sample_rate,
                audio_chunk_base64=base64.b64encode(chunk).decode("utf-8"),
                status=status,
                seq=seq,
                include_parameters=seq == 0,
            )
            await websocket.send(json.dumps(request))
            seq += 1
            if is_last_frame:
                break
            status = 1
            await asyncio.sleep(SHORT_IAT_FRAME_INTERVAL_SECONDS)

        if total_size == 0:
            request = build_short_iat_request(
                language=language,
                audio_encoding=audio_encoding,
                sample_rate=sample_rate,
                audio_chunk_base64="",
                status=2,
                seq=0,
                include_parameters=True,
            )
            await websocket.send(json.dumps(request))

    try:
        async with websockets.connect(url) as websocket:
            sender = asyncio.create_task(_send_audio_frames(websocket))
            try:
                async for message in websocket:
                    payload = json.loads(message)
                    header = payload.get("header") or {}
                    code = int(header.get("code", 0))
                    if code != 0:
                        message_text = header.get("message") or payload.get("message") or f"code={code}"
                        raise SpeechError(f"XFYun short ASR failed: {normalize_short_iat_error_message(message_text)}")

                    result = ((payload.get("payload") or {}).get("result") or {})
                    result_text_base64 = result.get("text")
                    if result_text_base64:
                        sn, text, parsed = parse_short_iat_payload(result_text_base64)
                        raw_results.append(parsed)
                        pgs = parsed.get("pgs")
                        if pgs == "rpl":
                            rg = parsed.get("rg") or []
                            if len(rg) == 2:
                                for index in range(int(rg[0]), int(rg[1]) + 1):
                                    content_map.pop(index, None)
                        content_map[sn] = text
                        if text:
                            segments.append({"sn": sn, "text": text, "pgs": pgs})

                    if int(header.get("status", 0)) == 2:
                        break
            finally:
                await sender
    except SpeechError:
        raise
    except Exception as exc:
        raise SpeechError(str(exc)) from exc

    full_text = "".join(content_map[index] for index in sorted(content_map))
    raw = {"results": raw_results, "endpoint": endpoint}
    return full_text, segments, raw


def _ifasr_llm_signature(params: dict[str, str], api_secret: str) -> str:
    items = []
    for key in sorted(params.keys()):
        value = params[key]
        if value is not None and value != "":
            items.append(f"{key}={quote(str(value), safe='')}")
    base_string = "&".join(items)
    return base64.b64encode(
        hmac.new(api_secret.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")


async def submit_ifasr_llm_job(audio_bytes: bytes, filename: str, duration_ms: int, language: str) -> tuple[str, int]:
    settings = get_settings()
    signature_random = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    params = {
        "appId": settings.XFYUN_APP_ID,
        "accessKeyId": settings.XFYUN_API_KEY,
        "dateTime": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "signatureRandom": signature_random,
        "fileSize": str(len(audio_bytes)),
        "fileName": filename,
        "duration": str(duration_ms),
        "language": language,
    }
    signature = _ifasr_llm_signature(params, settings.XFYUN_API_SECRET)
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://office-api-ist-dx.iflyaisol.com/v2/upload",
            params=params,
            headers={"Content-Type": "application/octet-stream", "signature": signature},
            content=audio_bytes,
        )
        response.raise_for_status()
        payload = response.json()
    if payload.get("code") != "000000":
        raise SpeechError(payload.get("descInfo", "XFYun IFASR LLM upload failed."))
    content = payload.get("content") or {}
    return content["orderId"], int(content.get("taskEstimateTime", 0))


async def poll_ifasr_llm_result(order_id: str, result_type: str = "transfer") -> dict:
    settings = get_settings()
    deadline = time.monotonic() + settings.XFYUN_SPEECH_POLL_TIMEOUT_SECONDS
    signature_random = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    async with httpx.AsyncClient(timeout=120) as client:
        while time.monotonic() < deadline:
            params = {
                "accessKeyId": settings.XFYUN_API_KEY,
                "dateTime": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
                "signatureRandom": signature_random,
                "orderId": order_id,
                "resultType": result_type,
            }
            signature = _ifasr_llm_signature(params, settings.XFYUN_API_SECRET)
            response = await client.post(
                "https://office-api-ist-dx.iflyaisol.com/v2/getResult",
                params=params,
                headers={"Content-Type": "application/json", "signature": signature},
                json={},
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") != "000000":
                raise SpeechError(payload.get("descInfo", "XFYun IFASR LLM query failed."))

            content = payload.get("content") or {}
            order_info = content.get("orderInfo") or {}
            status = order_info.get("status")
            if status == 4:
                return content
            if order_info.get("failType", 0):
                raise SpeechError(f"XFYun transcription failed with failType={order_info['failType']}.")
            await asyncio.sleep(settings.XFYUN_SPEECH_POLL_INTERVAL_SECONDS)
    raise SpeechError("XFYun transcription polling timed out.")


def extract_text_from_order_result(order_result: str | dict) -> tuple[str, list[dict]]:
    if isinstance(order_result, str):
        parsed = json.loads(order_result)
    else:
        parsed = order_result

    segments: list[dict] = []
    texts: list[str] = []
    for item in parsed.get("lattice2") or parsed.get("lattice") or []:
        json_best = item.get("json_1best")
        if isinstance(json_best, str):
            json_best = json.loads(json_best)
        st = (json_best or {}).get("st", {})
        words = []
        for rt in st.get("rt", []):
            for ws in rt.get("ws", []):
                for candidate in ws.get("cw", []):
                    word = candidate.get("w", "")
                    if word:
                        words.append(word)
                        break
        segment_text = "".join(words).strip()
        if segment_text:
            texts.append(segment_text)
            segments.append(
                {
                    "text": segment_text,
                    "begin": int(item.get("begin") or st.get("bg") or 0),
                    "end": int(item.get("end") or st.get("ed") or 0),
                    "speaker": item.get("spk"),
                }
            )
    return "".join(texts), segments


def assemble_ws_auth_url(url: str, api_key: str, api_secret: str) -> str:
    index = url.index("://")
    host = url[index + 3 :]
    schema = url[: index + 3]
    path_index = host.index("/")
    path = host[path_index:]
    host = host[:path_index]

    date = format_date_time(mktime(datetime.now().timetuple()))
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
    return f"{schema}{host}{path}?{urlencode({'authorization': authorization, 'date': date, 'host': host})}"


async def synthesize_tts_audio(text: str, voice: str, speed: int, volume: int, pitch: int, audio_format: str, sample_rate: int) -> tuple[bytes, dict]:
    settings = get_settings()
    url = assemble_ws_auth_url("wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6", settings.XFYUN_API_KEY, settings.XFYUN_API_SECRET)
    request_body = {
        "header": {
            "app_id": settings.XFYUN_APP_ID,
            "status": 2,
        },
        "parameter": {
            "tts": {
                "vcn": voice,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "audio": {
                    "encoding": "lame" if audio_format == "mp3" else "raw",
                    "sample_rate": sample_rate,
                    "channels": 1,
                    "bit_depth": 16,
                },
            }
        },
        "payload": {
            "text": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "plain",
                "status": 2,
                "seq": 0,
                "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
            }
        },
    }
    audio_chunks: list[bytes] = []
    result_meta = {"format": audio_format, "sample_rate": sample_rate, "voice": voice}
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(request_body))
        async for message in websocket:
            payload = json.loads(message)
            if payload.get("code", 0) != 0:
                raise SpeechError(payload.get("message", "XFYun Super TTS failed."))
            audio_data = payload.get("payload", {}).get("audio", {}).get("audio")
            if audio_data:
                audio_chunks.append(base64.b64decode(audio_data))
            if payload.get("payload", {}).get("audio", {}).get("status") == 2:
                break
    return b"".join(audio_chunks), result_meta
