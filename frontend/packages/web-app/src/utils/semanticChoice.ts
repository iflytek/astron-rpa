interface NodeKey {
  key: string | number
  atomics?: NodeKey[]
}

export function isSemanticChoiceAvailable(tree: NodeKey[]): boolean {
  return tree.some(node => node.key === 'SemanticAI.choose' || isSemanticChoiceAvailable(node.atomics ?? []))
}

/** Checks availability without changing saved nodes or preventing the flow from opening. */
export async function getSemanticChoiceWarning(nodes: NodeKey[], load: () => Promise<unknown>) {
  if (!isSemanticChoiceAvailable(nodes))
    return null

  try {
    const capability = await load()
    if (!capability || typeof capability !== 'object' || !('enabled' in capability) || typeof capability.enabled !== 'boolean')
      return { key: 'semanticChoiceUnavailable', reason: '' }
    if (capability.enabled)
      return null
    const reason = 'reason' in capability && typeof capability.reason === 'string' && capability.reason.trim()
      ? capability.reason
      : 'SEMANTIC_CHOICE_ENABLED, SEMANTIC_CHOICE_PROVIDER'
    return { key: 'semanticChoiceDisabled', reason }
  }
  catch {
    return { key: 'semanticChoiceUnavailable', reason: '' }
  }
}
