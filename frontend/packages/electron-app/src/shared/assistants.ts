export type AssistantModelOverride = {
  providerId: string
  model: string
}

export type AssistantToolPolicy = "assigned_only" | "allow_assigned" | "no_tools"
export type GroupRoomCollaborationMode = "auto" | "pipeline" | "race" | "debate"

export type AssistantRecord = {
  id: string
  name: string
  description: string | null
  avatar: string | null
  color: string | null
  systemPrompt: string | null
  defaultModel: AssistantModelOverride | null
  skillIds: string[]
  toolIds: string[]
  toolPolicy: AssistantToolPolicy
  createdAt: string
  updatedAt: string
}

export type AssistantSessionRecord = {
  id: string
  assistantId: string
  runtimeSessionId: string
  title: string | null
  createdAt: string
  updatedAt: string
}

export type GroupRoomRecord = {
  id: string
  name: string
  description: string | null
  memberAssistantIds: string[]
  coordinatorPrompt: string | null
  collaborationMode: GroupRoomCollaborationMode
  createdAt: string
  updatedAt: string
}

export type GroupRoomSessionRecord = {
  id: string
  groupRoomId: string
  runtimeSessionId: string
  title: string | null
  createdAt: string
  updatedAt: string
}

export type OpencodeSkillRecord = {
  id: string
  type: "opencode_skill"
  name: string
  description: string
  source: "project" | "global" | "remote"
}

export type RuntimeSkillDiscoveryState = {
  skills: OpencodeSkillRecord[]
  unavailable: boolean
  error: string | null
}
