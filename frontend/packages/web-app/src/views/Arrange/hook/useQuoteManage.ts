import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'

export function quoteManage(currentItem, callback: (args: any) => void, pickType = '') {
  console.time('quoteManage')
  const worker = new Worker(new URL('@/worker/quote.ts', import.meta.url))
  const processStore = useProcessStore()
  const obj = {}
  const list = []
  processStore.processList.filter(i => i.resourceCategory === 'process').forEach((item) => {
    list.push({
      resourceId: item.resourceId,
      name: item.name,
    })
    obj[item.resourceId] = useProjectDocStore().userFlowNode(item.resourceId)
  })
  worker.postMessage({
    key: 'quoteManage',
    params: {
      processList: list,
      nodes: JSON.stringify(obj),
      pickType,
      quotedId: currentItem.id,
    },
  })

  worker.onmessage = (e) => {
    console.timeEnd('quoteManage')
    const { params } = e.data
    console.log('params', params)
    callback(params)
    worker.terminate()
  }
}

export function gainUnUseQuote(callback: (args: any) => void, pickType = '') {
  console.time('unUseQuoteManage')
  const worker = new Worker(new URL('@/worker/quote.ts', import.meta.url))
  const processStore = useProcessStore()
  const obj = {}
  const list = []
  processStore.processList.filter(i => i.resourceCategory === 'process').forEach((item) => {
    list.push({
      resourceId: item.resourceId,
      name: item.name,
    })
    obj[item.resourceId] = useProjectDocStore().userFlowNode(item.resourceId)
  })
  worker.postMessage({
    key: 'unUseQuoteManage',
    params: {
      processList: list,
      nodes: JSON.stringify(obj),
      pickType,
    },
  })

  worker.onmessage = (e) => {
    console.timeEnd('unUseQuoteManage')
    const { params } = e.data
    callback(params)
    worker.terminate()
  }
}
