/* eslint-disable */
self.addEventListener('message', (event) => {
    console.log('worker on message: ', event);
    const { data } = event;
    quoteWorkerhandler(data.key, data.params);
});

const quoteFuncMap = {
    quoteManage,
    unUseQuoteManage,
}

function quoteWorkerhandler(key: string, params: any) {
    quoteFuncMap[key](params);
}

function quoteManage(params: { processList: { resourceId: string; name: string }[], pickType: string, nodes: any, quotedId: string }) {
    const { processList, nodes, quotedId, pickType } = params
    const userNodes = JSON.parse(nodes)
    const flowItems = processList.map(item => {
        const findItem = userNodes[item.resourceId].reduce((acc, node, index) => {
            const flag = node.inputList.some((i) => {
                if (i.formType.type === "PICK" && Array.isArray(i.value) && (i.value.find(v => v.data === quotedId))) {
                    if (i.formType.params.use === pickType) return true
                    return true
                }
                return false
            })
            if (flag) {
                acc.push({
                    ...node,
                    index: index + 1,
                })
            }
            return acc
        }, [])
        return {
            processId: item.resourceId,
            processName: item.name,
            atoms: findItem,
        }
    })
    self.postMessage({
        params: flowItems.filter(i => i.atoms.length > 0)
    })
}

function unUseQuoteManage(params: { processList: RPA.Flow.ProcessModule[], pickType: string, nodes: any }) {
    const { processList, nodes, pickType } = params
    let useImgs = []
    const userNodes = JSON.parse(nodes)
    processList.forEach(item => {
        userNodes[item.resourceId].forEach((node) => {
            node.inputList.forEach((i) => {
                if (i.formType.type === "PICK" && i.formType.params.use === pickType && Array.isArray(i.value)) {
                    useImgs = useImgs.concat(i.value.filter(v => v.type === 'element' && v.value).map((v) => { return { id: v.data, name: v.value } }))
                }
            })
        })
    })
    self.postMessage({
        params: useImgs.map(i => i.id)
    })
}