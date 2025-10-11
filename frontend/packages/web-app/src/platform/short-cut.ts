import type { ShortCutManager } from '@rpa/shared/platform'

const ShortCut: ShortCutManager = {
  register(_shortKey: string, _handler: any) {},

  unregister(_shortKey: string) {},

  unregisterAll() {},

  regeisterToolbar() {},

  regeisterFlow() {},
}

export default ShortCut
