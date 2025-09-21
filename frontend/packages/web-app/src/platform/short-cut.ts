import type { ShortCutManager } from '@rpa/types'

const ShortCut: ShortCutManager = {
  register(_shortKey: string, _handler: any) {},

  unregister(_shortKey: string) {},

  unregisterAll() {},

  regeisterToolbar() {},

  regeisterFlow() {},
}

export default ShortCut
