type OpencodeWindowApi = {
  getBootstrap?: () => Promise<unknown>
  getSession?: (sessionId: string) => Promise<unknown>
  createSession?: (payload: unknown) => Promise<unknown>
  renameSession?: (payload: unknown) => Promise<unknown>
  deleteSession?: (sessionId: string) => Promise<unknown>
  sendMessage?: (payload: unknown) => Promise<unknown>
  getSettings?: () => Promise<unknown>
  saveProvider?: (input: unknown) => Promise<unknown>
  saveDefaultModel?: (input: unknown) => Promise<unknown>
  saveAssistant?: (input: unknown) => Promise<unknown>
  deleteAssistant?: (id: string) => Promise<unknown>
  listGroupRooms?: () => Promise<unknown>
  saveGroupRoom?: (input: unknown) => Promise<unknown>
  deleteGroupRoom?: (id: string) => Promise<unknown>
  listSkills?: () => Promise<unknown>
  importSkill?: () => Promise<unknown>
  deleteSkill?: (skillId: string) => Promise<unknown>
  onRuntimeEvent?: (listener: (event: unknown) => void) => () => void
}

declare global {
  interface Window {
    opencodeApi?: OpencodeWindowApi
  }
}

export {}
