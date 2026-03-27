import { assistantGroups, sessionDetails } from '../mock'

import type {
  AIStudioBootstrap,
  AIStudioCardActionPayload,
  AIStudioChoiceSubmissionPayload,
  AIStudioParamSubmissionPayload,
  AIStudioProvider,
  AIStudioSendMessagePayload,
  AIStudioSessionMutationResult,
} from '../contracts'
import type {
  StudioArtifact,
  StudioAction,
  StudioChatCard,
  StudioChoiceOption,
  StudioPlanStep,
  StudioSessionDetail,
  StudioSessionStatus,
  StudioWorkItem,
} from '../types'

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function wait(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function findFallbackSession(): StudioSessionDetail {
  return sessionDetails['finance-q3'] || Object.values(sessionDetails)[0]
}

const runtimeSessionDetails: Record<string, StudioSessionDetail> = clone(sessionDetails)

function ensureRuntimeSession(sessionId: string) {
  if (!runtimeSessionDetails[sessionId]) {
    runtimeSessionDetails[sessionId] = clone(sessionDetails[sessionId] || findFallbackSession())
    runtimeSessionDetails[sessionId].id = sessionId
  }
  return runtimeSessionDetails[sessionId]
}

function sessionStatusLabel(status: StudioSessionStatus) {
  switch (status) {
    case 'running':
      return '处理中'
    case 'waiting-confirm':
      return '待确认'
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    default:
      return '空闲'
  }
}

function resolveSessionAssistantId(session: StudioSessionDetail) {
  if (session.id.startsWith('office'))
    return 'office'
  if (session.id.startsWith('code'))
    return 'code'
  if (session.id.startsWith('data'))
    return 'data'
  return 'finance'
}

function mentionDisplayName(id: string) {
  if (id === 'office')
    return '办公助手'
  if (id === 'finance')
    return '财务助手'
  if (id === 'code')
    return '代码助手'
  if (id === 'data')
    return '数据分析师'
  return id
}

function skillDisplayName(id: string) {
  if (id === 'summary')
    return '/总结'
  if (id === 'report')
    return '/生成报告'
  if (id === 'code')
    return '/分析代码'
  return id
}

function collaborationModeLabel(mode?: StudioSessionDetail['collaborationMode']) {
  if (mode === 'pipeline')
    return '流水线'
  if (mode === 'race')
    return '赛马'
  if (mode === 'debate')
    return '会审'
  return '自动'
}

function describeSendPayload(payload: AIStudioSendMessagePayload) {
  const parts: string[] = []

  if (payload.mentions?.length)
    parts.push(`已提及 ${payload.mentions.map(mentionDisplayName).join('、')}`)

  if (payload.skills?.length)
    parts.push(`按 ${payload.skills.map(skillDisplayName).join('、')} 模式处理`)

  return parts.length ? `，${parts.join('，')}` : ''
}

function setSessionStatus(session: StudioSessionDetail, status: StudioSessionStatus, summary?: string) {
  session.status = status
  session.headerTag = sessionStatusLabel(status)
  session.run = {
    id: session.run?.id || `run-${Date.now()}`,
    status,
    label: sessionStatusLabel(status),
    summary,
  }
}

function nextTimelineOrder(session: StudioSessionDetail) {
  const messageOrders = session.messages.map((message, index) => message.order ?? index)
  const cardBase = session.messages.length
  const cardOrders = (session.chatCards || []).map((card, index) => card.order ?? (cardBase + index))
  return Math.max(-1, ...messageOrders, ...cardOrders) + 1
}

function appendAssistantTextCard(session: StudioSessionDetail, content: string, card?: Partial<Extract<StudioChatCard, { type: 'text' }>>) {
  session.chatCards = session.chatCards || []
  session.chatCards.push({
    id: card?.id || `${session.id}-reply-${Date.now()}`,
    type: 'text',
    assistantId: card?.assistantId || resolveSessionAssistantId(session),
    assistantName: card?.assistantName || session.assistantName,
    assistantBadge: card?.assistantBadge || session.headerBadge,
    time: '刚刚',
    tone: card?.tone || 'default',
    content,
    order: card?.order ?? nextTimelineOrder(session),
  })
}

function clearFollowUpSuggestions(session: StudioSessionDetail) {
  session.options = []
  session.promptTitle = undefined
  session.promptDescription = undefined
  session.chatCards = (session.chatCards || []).filter(card => card.type !== 'prompt-suggestions')
}

function officeFollowUpReply(content: string) {
  if (content.includes('总结这轮进展'))
    return '可以，我先把这轮进展、待办和待确认项整理成一版简要总结。'
  if (content.includes('待办清单'))
    return '好的，我会把当前结果整理成待办清单，并补齐负责人和截止时间。'
  if (content.includes('财务助手'))
    return '可以，我会把财务助手拉进来，一起复核这轮结果里的数据口径和风险项。'
  return '收到，我会按这条追问继续推进当前会话。'
}

function findCardIndex(session: StudioSessionDetail, cardId: string) {
  return (session.chatCards || []).findIndex(card => card.id === cardId)
}

function findCard(session: StudioSessionDetail, cardId: string): StudioChatCard | null
function findCard<TType extends StudioChatCard['type']>(
  session: StudioSessionDetail,
  cardId: string,
  type: TType,
): Extract<StudioChatCard, { type: TType }> | null
function findCard<TType extends StudioChatCard['type']>(
  session: StudioSessionDetail,
  cardId: string,
  type?: TType,
) {
  const card = (session.chatCards || []).find(item => item.id === cardId)
  if (!card)
    return null
  if (type && card.type !== type)
    return null
  if (type)
    return card as Extract<StudioChatCard, { type: TType }>
  return card
}

function replaceCard(session: StudioSessionDetail, cardId: string, nextCard: StudioChatCard) {
  const index = findCardIndex(session, cardId)
  if (index === -1)
    return
  session.chatCards = session.chatCards || []
  session.chatCards.splice(index, 1, nextCard)
}

function removeCard(session: StudioSessionDetail, cardId: string) {
  const index = findCardIndex(session, cardId)
  if (index === -1)
    return
  session.chatCards = session.chatCards || []
  session.chatCards.splice(index, 1)
}

function updateApprovalCard(session: StudioSessionDetail, cardId: string, next: {
  title?: string
  description?: string
  levelTag?: string
}) {
  const card = findCard(session, cardId, 'approval')
  if (!card)
    return
  replaceCard(session, cardId, {
    ...card,
    title: next.title || card.title,
    description: next.description || card.description,
    levelTag: next.levelTag || card.levelTag,
    actions: [],
  })
}

function updateErrorBoundaryCard(session: StudioSessionDetail, cardId: string, next: {
  title?: string
  description?: string
  suggestions?: string[]
}) {
  const card = findCard(session, cardId, 'error-boundary')
  if (!card)
    return
  replaceCard(session, cardId, {
    ...card,
    title: next.title || card.title,
    description: next.description || card.description,
    suggestions: next.suggestions || card.suggestions,
    actions: [],
  })
}

function updateDraftReviewCard(session: StudioSessionDetail, cardId: string, next: {
  description?: string
  actions?: StudioAction[]
}) {
  const card = findCard(session, cardId, 'draft-review')
  if (!card)
    return
  replaceCard(session, cardId, {
    ...card,
    description: next.description || card.description,
    actions: next.actions ?? card.actions,
  })
}

function updateArtifact(session: StudioSessionDetail, artifactId: string, mapper: (artifact: StudioArtifact) => StudioArtifact) {
  session.artifacts = session.artifacts.map(artifact => artifact.id === artifactId ? mapper(artifact) : artifact)
}

function updatePlanStep(session: StudioSessionDetail, cardId: string, stepId: string, mapper: (step: StudioPlanStep) => StudioPlanStep) {
  const card = findCard(session, cardId, 'plan')
  if (!card)
    return
  replaceCard(session, cardId, {
    ...card,
    steps: card.steps.map(step => step.id === stepId ? mapper(step) : step),
  })
}

function updateKnowledgeSourceStatus(session: StudioSessionDetail, cardId: string, sourceId: string, status: string, detail: string) {
  const card = findCard(session, cardId, 'knowledge-sources')
  if (!card)
    return
  replaceCard(session, cardId, {
    ...card,
    sources: card.sources.map(source => source.id === sourceId
      ? { ...source, status: status as typeof source.status, detail }
      : source),
  })
}

function updateWorkItems(items: StudioWorkItem[] | undefined, due: string) {
  return (items || []).map(item => ({ ...item, due }))
}

function updateDueDateRows(rows: { id: string, cells: string[], tone?: 'default' | 'danger' | 'success' }[] | undefined, due: string) {
  return (rows || []).map(row => ({
    ...row,
    cells: row.cells.map((cell, index) => index === 2 ? due : cell),
  }))
}

function updateOfficeDeadline(session: StudioSessionDetail, due: string) {
  const meetingCard = findCard(session, 'office-meeting', 'meeting-recap')
  if (meetingCard) {
    replaceCard(session, 'office-meeting', {
      ...meetingCard,
      actionItems: updateWorkItems(meetingCard.actionItems, due),
    })
  }

  const workItemsCard = findCard(session, 'office-work-items', 'work-item-list')
  if (workItemsCard) {
    replaceCard(session, 'office-work-items', {
      ...workItemsCard,
      items: updateWorkItems(workItemsCard.items, due),
    })
  }

  const artifactCard = findCard(session, 'office-artifact', 'artifact-preview')
  if (artifactCard?.preview?.kind === 'table') {
    replaceCard(session, 'office-artifact', {
      ...artifactCard,
      preview: {
        ...artifactCard.preview,
        rows: updateDueDateRows(artifactCard.preview.rows, due),
      },
    })
  }

  if (session.workspacePreview?.kind === 'table') {
    session.workspacePreview = {
      ...session.workspacePreview,
      rows: updateDueDateRows(session.workspacePreview.rows, due),
    }
  }

  updateArtifact(session, 'office-artifact-1', artifact => ({
    ...artifact,
    preview: artifact.preview?.kind === 'table'
      ? {
          ...artifact.preview,
          rows: updateDueDateRows(artifact.preview.rows, due),
        }
      : artifact.preview,
  }))
}

function selectedChoiceLabel(card: Extract<StudioChatCard, { type: 'choice-form' }>, optionId: string) {
  const option = card.options.find(item => item.id === optionId)
  return option?.label || optionId
}

function choiceResponse(session: StudioSessionDetail, card: Extract<StudioChatCard, { type: 'choice-form' }>, option: StudioChoiceOption) {
  if (session.id === 'data-growth') {
    session.workspacePreview = {
      kind: 'summary',
      fileName: 'growth_weekly_report.md',
      status: '已更新',
      title: '用户增长周报',
      description: `已按“${option.label}”重新整理本周增长分析焦点。`,
      items: [
        { label: '分析路径', value: option.label, tone: 'success' },
        { label: '输出重点', value: option.description, tone: 'default' },
        { label: '下一步', value: '补充趋势图、异常说明和渠道归因结论', tone: 'default' },
      ],
    }
    updateArtifact(session, 'growth-report-artifact', artifact => ({
      ...artifact,
      tag: '已更新',
      tagTone: 'success',
    }))
    appendAssistantTextCard(session, `已确认分析路径：${option.label}`, {
      assistantId: card.assistantId,
      assistantName: card.assistantName,
      assistantBadge: card.assistantBadge,
    })
    return
  }

  appendAssistantTextCard(session, `已按“${option.label}”继续处理当前任务。`, {
    assistantId: card.assistantId,
    assistantName: card.assistantName,
    assistantBadge: card.assistantBadge,
  })
}

function applyOfficeConnect(session: StudioSessionDetail) {
  const connectCard = findCard(session, 'office-connect', 'connect-auth')
  if (connectCard) {
    replaceCard(session, 'office-connect', {
      ...connectCard,
      description: 'CRM 商机看板已连接成功，当前会话可继续读取本周重点商机负责人和预计签约时间。',
      statusTag: '已连接',
      actions: [
        { id: 'office-connect-reauth', label: '重新授权', tone: 'secondary' },
      ],
    })
  }

  updateKnowledgeSourceStatus(
    session,
    'office-sources',
    'office-source-4',
    'connected',
    '已连接，正在补齐重点商机负责人和预计签约时间',
  )

  updatePlanStep(session, 'office-plan', 'office-plan-2', step => ({
    ...step,
    status: 'done',
    description: 'CRM 商机负责人和预计签约时间已同步到当前 briefing',
  }))
  updatePlanStep(session, 'office-plan', 'office-plan-3', step => ({
    ...step,
    status: 'running',
  }))
  setSessionStatus(session, 'waiting-confirm', 'CRM 上下文已同步')
}

function applyOfficeCardAction(session: StudioSessionDetail, actionId: string) {
  switch (actionId) {
    case 'office-connect-now':
      applyOfficeConnect(session)
      return
    case 'office-connect-later':
      replaceCard(session, 'office-connect', {
        ...(findCard(session, 'office-connect', 'connect-auth')!),
        statusTag: '稍后处理',
        description: '已记录稍后连接 CRM，当前先基于已有资料继续整理会后跟进。',
        actions: [
          { id: 'office-connect-now', label: '继续连接', tone: 'secondary' },
        ],
      })
      setSessionStatus(session, 'waiting-confirm', '等待更多上下文')
      return
    case 'office-boundary-continue':
      removeCard(session, 'office-boundary')
      setSessionStatus(session, 'waiting-confirm', '已采用受限模式继续')
      return
    case 'office-boundary-request':
      updateErrorBoundaryCard(session, 'office-boundary', {
        title: '已生成权限申请',
        description: '已整理权限申请说明，待管理员补充 Calendar private events scope 后可继续。',
        suggestions: ['等待管理员补充权限', '当前先按受限模式继续处理'],
      })
      setSessionStatus(session, 'waiting-confirm', '已生成权限申请')
      return
    case 'office-schedule-create': {
      const card = findCard(session, 'office-schedule', 'schedule')
      if (card) {
        replaceCard(session, 'office-schedule', {
          ...card,
          statusTag: '已创建',
          nextRun: '2026-03-24 18:00',
          actions: [
            { id: 'office-schedule-adjust', label: '调整计划', tone: 'secondary' },
          ],
        })
      }
      setSessionStatus(session, 'waiting-confirm', '定时任务已创建')
      return
    }
    case 'office-schedule-skip':
      replaceCard(session, 'office-schedule', {
        ...(findCard(session, 'office-schedule', 'schedule')!),
        statusTag: '已跳过',
        description: '已跳过自动跟进任务创建，保留当前会后行动表。',
        actions: [
          { id: 'office-schedule-create', label: '重新创建', tone: 'secondary' },
        ],
      })
      setSessionStatus(session, 'waiting-confirm', '已跳过自动化')
      return
    case 'office-draft-edit':
      updateDraftReviewCard(session, 'office-draft', {
        description: '你可以继续补充口径，我会同步修改会后邮件草稿。',
      })
      setSessionStatus(session, 'waiting-confirm', '待继续修改草稿')
      return
    case 'office-draft-send':
      updateArtifact(session, 'office-artifact-2', artifact => ({
        ...artifact,
        tag: '已发送',
        tagTone: 'success',
      }))
      updateDraftReviewCard(session, 'office-draft', {
        description: '会后邮件草稿已发送，并同步了销售负责人跟进要求。',
        actions: [
          { id: 'office-draft-edit', label: '查看草稿', tone: 'secondary' },
        ],
      })
      setSessionStatus(session, 'waiting-confirm', '草稿已发送')
      return
    case 'office-approval-allow':
    case 'office-approval-always':
      updateArtifact(session, 'office-artifact-1', artifact => ({ ...artifact, tag: '已完成', tagTone: 'success' }))
      updateArtifact(session, 'office-artifact-2', artifact => ({ ...artifact, tag: '已发送', tagTone: 'success' }))
      updateArtifact(session, 'office-artifact-3', artifact => ({ ...artifact, tag: '已完成', tagTone: 'success' }))
      updateApprovalCard(session, 'office-approval', {
        description: '已发送跟进邮件，并同步创建 3 条待办到任务中心。',
        levelTag: actionId === 'office-approval-always' ? '始终允许' : '已执行',
      })
      setSessionStatus(session, 'completed', '会后动作已完成')
      return
    case 'office-approval-reject':
      updateApprovalCard(session, 'office-approval', {
        description: '已取消执行，当前内容保留在工作空间中供你继续修改。',
        levelTag: '已拒绝',
      })
      setSessionStatus(session, 'waiting-confirm', '等待新的确认')
      return
    default:
      setSessionStatus(session, 'waiting-confirm', '已处理卡片动作')
  }
}

function applyCardAction(session: StudioSessionDetail, payload: AIStudioCardActionPayload) {
  if (session.id === 'office-briefing') {
    applyOfficeCardAction(session, payload.actionId)
    return
  }

  const normalizedAction = payload.actionId
  if (payload.cardId === 'audit-approval') {
    updateApprovalCard(session, 'audit-approval', {
      description: normalizedAction.includes('allow') || normalizedAction.includes('允许')
        ? '已允许执行修复补丁，后续将继续同步权限修复结果。'
        : '已拒绝执行修复补丁，当前保留风险记录等待新的确认。',
      levelTag: normalizedAction.includes('always') || normalizedAction.includes('始终')
        ? '始终允许'
        : normalizedAction.includes('allow') || normalizedAction.includes('允许')
            ? '已允许'
            : '已拒绝',
    })
  }
  setSessionStatus(session, 'waiting-confirm', '动作已处理')
}

function applyChoiceSubmission(session: StudioSessionDetail, payload: AIStudioChoiceSubmissionPayload) {
  const card = findCard(session, payload.cardId, 'choice-form')
  if (!card)
    return

  const label = selectedChoiceLabel(card, payload.optionId)
  removeCard(session, payload.cardId)
  choiceResponse(session, card, {
    id: payload.optionId,
    label,
    description: card.options.find(option => option.id === payload.optionId)?.description || '',
  })
  setSessionStatus(session, 'waiting-confirm', '选项已确认')
}

function applyParamSubmission(session: StudioSessionDetail, payload: AIStudioParamSubmissionPayload) {
  const card = findCard(session, payload.cardId, 'param-form')
  if (!card)
    return

  removeCard(session, payload.cardId)

  if (session.id === 'office-briefing') {
    const dueDate = payload.values.deadline || '待补充'
    const focusMap: Record<string, string> = {
      sales: '销售风险',
      delivery: '交付排期',
      all: '全部同步',
    }
    updateOfficeDeadline(session, dueDate)
    appendAssistantTextCard(session, `统一截止日期已更新为 ${dueDate}，我会按“${focusMap[payload.values.focus] || '当前口径'}”整理 recap、follow-up 和邮件草稿。`, {
      assistantId: card.assistantId,
      assistantName: card.assistantName,
      assistantBadge: card.assistantBadge,
    })
    updatePlanStep(session, 'office-plan', 'office-plan-3', step => ({ ...step, status: 'running' }))
    setSessionStatus(session, 'waiting-confirm', '参数已更新')
    return
  }

  appendAssistantTextCard(session, `已补齐参数，继续处理“${session.headerTitle}”。`, {
    assistantId: card.assistantId,
    assistantName: card.assistantName,
    assistantBadge: card.assistantBadge,
  })
  setSessionStatus(session, 'waiting-confirm', '参数已更新')
}

function applySendMessage(session: StudioSessionDetail, payload: AIStudioSendMessagePayload) {
  clearFollowUpSuggestions(session)

  session.messages.push({
    id: `${session.id}-user-${Date.now()}`,
    role: 'user',
    content: payload.content,
    time: '刚刚',
    order: nextTimelineOrder(session),
  })

  const payloadSuffix = describeSendPayload(payload)

  if (session.id === 'office-briefing') {
    appendAssistantTextCard(session, `${officeFollowUpReply(payload.content)}${payloadSuffix}`, {
      assistantId: 'office',
      assistantName: '办公助手',
      assistantBadge: '办',
    })
    if (payload.content.includes('待办清单')) {
      updateArtifact(session, 'office-artifact-1', artifact => ({
        ...artifact,
        summary: '经营例会会后行动表已按最新追问整理为待办清单。',
      }))
    }
    if (payload.content.includes('总结这轮进展')) {
      updateArtifact(session, 'office-artifact-3', artifact => ({
        ...artifact,
        summary: '经营例会 recap 已补充本轮进展摘要与待确认项。',
      }))
    }
    if (payload.content.includes('财务助手')) {
      appendAssistantTextCard(session, '财务助手已加入本轮协作，会继续补充数据口径和风险复核意见。', {
        assistantId: 'finance',
        assistantName: '财务助手',
        assistantBadge: '财',
        tone: 'subtle',
      })
    }
    setSessionStatus(session, 'waiting-confirm', '已发送追问')
    return
  }

  if (session.mode === 'group') {
    const coordinatorId = session.coordinatorAssistantId || 'coordinator'
    const collaborationText = collaborationModeLabel(session.collaborationMode)
    const participantIds = session.participantAssistantIds || []
    const nextCompleted = Math.min((session.collaborationSummary?.completedTasks || 0) + 1, Math.max(1, participantIds.length))
    const totalTasks = Math.max(2, participantIds.length + 1)
    session.collaborationState = nextCompleted >= totalTasks - 1 ? 'converging' : 'executing'
    session.collaborationSummary = {
      activeTasks: Math.max(totalTasks - nextCompleted, 1),
      completedTasks: nextCompleted,
      blockedTasks: session.collaborationSummary?.blockedTasks || 0,
    }
    appendAssistantTextCard(session, `收到，我会以主 Agent 继续按「${collaborationText}」模式推进，并同步各助手阶段结果${payloadSuffix}。`, {
      assistantId: coordinatorId,
      assistantName: '主 Agent',
      assistantBadge: '主',
    })
    setSessionStatus(session, 'waiting-confirm', '主 Agent 已接管本轮协作')
    return
  }

  appendAssistantTextCard(session, `收到，我会把这条补充并入当前会话结果${payloadSuffix}。`)
  setSessionStatus(session, 'waiting-confirm', '已发送消息')
}

async function mutateSession(sessionId: string, mutate: (session: StudioSessionDetail) => void): Promise<AIStudioSessionMutationResult> {
  const session = clone(ensureRuntimeSession(sessionId))
  setSessionStatus(session, 'running', '正在整理最新输入')
  mutate(session)
  runtimeSessionDetails[sessionId] = session
  await wait(180)
  return {
    session: clone(session),
  }
}

export const mockAIStudioProvider: AIStudioProvider = {
  async getBootstrap(): Promise<AIStudioBootstrap> {
    return {
      assistantGroups: clone(assistantGroups),
      defaultSessionId: 'finance-q3',
    }
  },

  async getSessionDetail(sessionId: string): Promise<StudioSessionDetail> {
    return clone(ensureRuntimeSession(sessionId))
  },

  async sendMessage(payload: AIStudioSendMessagePayload): Promise<AIStudioSessionMutationResult> {
    return mutateSession(payload.sessionId, (session) => {
      applySendMessage(session, payload)
    })
  },

  async submitChoiceForm(payload: AIStudioChoiceSubmissionPayload): Promise<AIStudioSessionMutationResult> {
    return mutateSession(payload.sessionId, (session) => {
      applyChoiceSubmission(session, payload)
    })
  },

  async submitParamForm(payload: AIStudioParamSubmissionPayload): Promise<AIStudioSessionMutationResult> {
    return mutateSession(payload.sessionId, (session) => {
      applyParamSubmission(session, payload)
    })
  },

  async submitCardAction(payload: AIStudioCardActionPayload): Promise<AIStudioSessionMutationResult> {
    return mutateSession(payload.sessionId, (session) => {
      applyCardAction(session, payload)
    })
  },
}
