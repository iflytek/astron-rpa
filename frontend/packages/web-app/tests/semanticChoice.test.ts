import assert from 'node:assert/strict'
import { test } from 'vitest'

import { getSemanticChoiceWarning, isSemanticChoiceAvailable } from '../src/utils/semanticChoice.ts'

test('ordinary saved flows do not query capabilities', async () => {
  const warning = await getSemanticChoiceWarning([{ key: 'Browser.open' }], async () => { throw new Error('must not call') })
  assert.equal(warning, null)
})

test('disabled saved node is preserved and gives actionable reason', async () => {
  const nodes = [{ key: 'SemanticAI.choose', inputList: [{ value: 'saved input' }] }]
  const before = structuredClone(nodes)
  assert.deepEqual(await getSemanticChoiceWarning(nodes, async () => ({ enabled: false, reason: 'Set SEMANTIC_CHOICE_ENABLED=true' })), {
    key: 'semanticChoiceDisabled', reason: 'Set SEMANTIC_CHOICE_ENABLED=true',
  })
  assert.deepEqual(nodes, before)
})

test('enabled node opens without warning', async () => {
  assert.equal(await getSemanticChoiceWarning([{ key: 'SemanticAI.choose' }], async () => ({ enabled: true, reason: null })), null)
})

test('failed or malformed capability lookup warns without rejecting flow load', async () => {
  for (const load of [async () => { throw new Error('offline') }, async () => ({}), async () => ({ enabled: 'true' })]) {
    assert.deepEqual(await getSemanticChoiceWarning([{ key: 'SemanticAI.choose' }], load), { key: 'semanticChoiceUnavailable', reason: '' })
  }
})

test('missing reason uses a configuration fallback', async () => {
  assert.deepEqual(await getSemanticChoiceWarning([{ key: 'SemanticAI.choose' }], async () => ({ enabled: false, reason: null })), {
    key: 'semanticChoiceDisabled', reason: 'SEMANTIC_CHOICE_ENABLED, SEMANTIC_CHOICE_PROVIDER',
  })
})

test('favorite availability follows server tree, including nested categories', () => {
  assert.equal(isSemanticChoiceAvailable([]), false)
  assert.equal(isSemanticChoiceAvailable([{ key: 'ai', atomics: [{ key: 'SemanticAI.choose' }] }]), true)
  assert.equal(isSemanticChoiceAvailable([{ key: 'Browser.open' }]), false)
})
