import { sseRequest } from "./sse";
import http from "./http";

// 举报AI生成内容
export function aiFeedback<T>(data: T) {
  return http.post("/api/robot/feedback/submit", data);
}

export function cuaChatStream(
  message: string,
  onMessage: (data: string) => void,
  onError: (err: any) => void,
  onComplete?: () => void,
  signal?: AbortSignal,
) {
  const path = "/api/rpa-ai-service/cua/chat/stream";
  const params = {
    messages: [{ role: "user", content: [{ type: "text", text: message }] }],
  };
  return sseRequest.post(
    path,
    params,
    (msg) => onMessage(msg.data),
    onError,
    { signal },
    onComplete,
  );
}
