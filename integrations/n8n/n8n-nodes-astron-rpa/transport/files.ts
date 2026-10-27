import { createHash } from "node:crypto";
import {
  FILE_LIMITS,
  safeFileName,
} from "../capabilities/shared/file-contract";
import { AstronError, object } from "../mapping/contracts";
import type { Connection } from "./mcp";
import { observedFetch } from "./correlation";

export interface FileMetadata {
  fileId: string;
  fileName: string;
  size: number;
  sha256: string;
  expiresAt: number;
}

export function fileId(value: unknown): string {
  if (
    typeof value !== "string" ||
    !/^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$/.test(value)
  )
    throw new AstronError("FILE_ID_INVALID");
  return value;
}

export function fileMetadata(value: unknown): FileMetadata {
  const result = object(value);
  fileId(result.fileId);
  safeFileName(result.fileName);
  if (
    !Number.isInteger(result.size) ||
    Number(result.size) < 0 ||
    Number(result.size) > FILE_LIMITS.maxFileBytes ||
    typeof result.sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(result.sha256) ||
    !Number.isFinite(result.expiresAt)
  )
    throw new AstronError("INVALID_FILE_RESPONSE");
  return result as unknown as FileMetadata;
}

export class FileConnection {
  private base: URL;

  constructor(
    private connection: Connection,
    private timeout: number,
    private fetcher: typeof fetch = fetch,
  ) {
    this.base = new URL(connection.endpoint);
    if (
      this.base.protocol !== "https:" ||
      this.base.username ||
      this.base.password ||
      this.base.search ||
      this.base.hash ||
      !/\/mcp\/?$/.test(this.base.pathname) ||
      !connection.apiKey.trim()
    )
      throw new AstronError("INVALID_ENDPOINT");
    this.base.pathname = this.base.pathname.replace(/mcp\/?$/, "files/");
  }

  private async request(
    path: string,
    init: RequestInit = {},
    binary = false,
  ): Promise<unknown> {
    let response: Response;
    try {
      response = await observedFetch(
        this.fetcher,
        new URL(path || this.base.pathname.slice(0, -1), this.base),
        {
          ...init,
          redirect: "error",
          signal: AbortSignal.timeout(this.timeout),
          headers: {
            Authorization: `Bearer ${this.connection.apiKey}`,
            ...(init.headers ?? {}),
          },
        },
        this.connection.correlation,
        "file",
      );
    } catch {
      throw new AstronError("FILE_TRANSFER_UNCONFIRMED", true);
    }
    const maximum = binary && response.ok ? FILE_LIMITS.maxFileBytes : 16384;
    const reader = response.body?.getReader();
    if (!reader) throw new AstronError("INVALID_FILE_RESPONSE");
    const chunks: Uint8Array[] = [];
    let size = 0;
    try {
      while (true) {
        const part = await reader.read();
        if (part.done) break;
        size += part.value.byteLength;
        if (size > maximum) throw new AstronError("FILE_TOO_LARGE");
        chunks.push(part.value);
      }
    } catch (error) {
      if (error instanceof AstronError) throw error;
      throw new AstronError("FILE_TRANSFER_UNCONFIRMED", true);
    } finally {
      await reader.cancel().catch(() => {});
      reader.releaseLock();
    }
    const data = Buffer.concat(chunks);
    if (!response.ok) {
      let code = "FILE_REQUEST_FAILED";
      try {
        const detail = object(JSON.parse(data.toString())).detail;
        const reported = object(detail).code;
        if (typeof reported === "string" && /^[A-Z_]{3,64}$/.test(reported))
          code = reported;
      } catch {
        /* Never copy remote diagnostics or credentials. */
      }
      throw new AstronError(code, response.status >= 500);
    }
    if (binary) return data;
    try {
      return JSON.parse(data.toString());
    } catch {
      throw new AstronError("INVALID_FILE_RESPONSE");
    }
  }

  async upload(name: string, data: Buffer, key: string): Promise<FileMetadata> {
    safeFileName(name);
    if (data.length > FILE_LIMITS.maxFileBytes)
      throw new AstronError("FILE_TOO_LARGE");
    const reserved = object(
      await this.request("", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName: name, uploadKey: key }),
      }),
    );
    const id = fileId(reserved.fileId);
    const result = fileMetadata(
      await this.request(`${id}/content`, {
        method: "PUT",
        headers: { "Content-Type": "application/octet-stream" },
        body: new Uint8Array(data),
      }),
    );
    if (
      result.fileId !== id ||
      result.fileName !== name ||
      result.size !== data.length ||
      result.sha256 !== createHash("sha256").update(data).digest("hex")
    )
      throw new AstronError("FILE_INTEGRITY_FAILED");
    return result;
  }

  async download(
    id: string,
  ): Promise<{ metadata: FileMetadata; data: Buffer }> {
    fileId(id);
    const metadata = fileMetadata(await this.request(id));
    if (metadata.fileId !== id) throw new AstronError("FILE_INTEGRITY_FAILED");
    const data = (await this.request(`${id}/content`, {}, true)) as Buffer;
    if (
      data.length !== metadata.size ||
      createHash("sha256").update(data).digest("hex") !== metadata.sha256
    )
      throw new AstronError("FILE_INTEGRITY_FAILED");
    return { metadata, data };
  }

  async delete(id: string): Promise<void> {
    const result = object(await this.request(fileId(id), { method: "DELETE" }));
    if (result.deleted !== true) throw new AstronError("INVALID_FILE_RESPONSE");
  }
}
