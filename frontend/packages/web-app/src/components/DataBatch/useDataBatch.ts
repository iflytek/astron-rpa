import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { cloneDeep } from 'lodash-es'
import { reactive, ref, watch } from 'vue'

import type { VxeGridProps } from '@/plugins/VxeTable'

import { generateColumnNames, generateSheetName, getUrlQueryField } from '@/utils/common'

import http from '@/api/http'
import { addElement, getElementDetail, getElementsAll, updateElement } from '@/api/resource'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { WINDOW_NAME } from '@/constants'
import { windowManager } from '@/platform'
import { useBatchPickStore } from '@/stores/useBatchPickStore'
import { usePickStore } from '@/stores/usePickStore'
import type { FormRules } from '@/types/common'
import type { BatchElementDataInfo, ColumnInfo, ElementInfo } from '@/types/databatch.d'
import { VISUALIZATION } from '@/views/Arrange/config/pick'

import { ColumnsKeys, Menus } from './config'

export function useDataBatch() {
  const { t } = useTranslation()
  const useBatchPick = useBatchPickStore()
  const usePick = usePickStore()
  const selectedColumnIndex = ref(-1) // 当前选中列的索引
  const menuItems = ref([]) // 当前选中列的菜单项
  const batchFormType = ref('') // 表单类型， similar: 相似抓取，table: 表格抓取
  const gridRef = ref(null) // 表格ref
  const formRef = ref(null) // 表单ref
  const batchModalRef = ref(null) // 批量操作弹窗ref
  const batchModalVisible = ref(false) // 批量操作弹窗是否显示
  const batchModalConfig = ref({}) // 批量操作弹窗配置
  const rules = reactive<FormRules>({ name: [{ message: t('dataBatch.tableNamePlaceholder'), trigger: 'blur' }] })
  const formState = reactive({ name: '' })
  const activeColumn = ref(null) // 当前激活的列
  const checkData = ref(false) // 查看当前数据
  const locale = getUrlQueryField('locale') || 'zh-CN'
  let isEdit = false // 是否是编辑状态
  let batchObject: ElementInfo // 抓取对象
  let batchElementData: BatchElementDataInfo // 抓取对象元素数据
  let tableElement = null // 表格元素信息
  // 表格列
  let columns: ColumnInfo[] = []
  // 表格数据
  let tableData: any[] = []
  // 表格列的数据
  let columnData: any[] = []
  let isHightLight = false // 是否高亮列

  // 单列 过滤出 menus
  watch(
    () => activeColumn.value,
    (newVal) => {
      // console.log('activeColumn ', newVal)
      let menus = batchTypeMenus(batchFormType.value)
      if (newVal) {
        const { filterConfig, colFilterConfig, colDataProcessConfig, isTable } = newVal // 获取处理条件
        menus = isTable ? menus.filter(menu => menu.key !== 'similarAdd') : menus
        menus.forEach((menu) => {
          if (menu.key === 'filterConfig' && filterConfig) {
            menu.active = filterConfig.length > 0
          }
          if (menu.key === 'colFilterConfig' && colFilterConfig) {
            menu.active = colFilterConfig.length > 0
          }
          if (menu.key === 'colDataProcessConfig' && colDataProcessConfig) {
            menu.children.forEach((child) => {
              const data = colDataProcessConfig.find(item => item.processType === child.key)
              if (data) {
                menu.active = data.isEnable === 1
                child.showEdit = data.parameters.length > 0
                child.checked = data.isEnable === 1
              }
              else {
                child.checked = false
              }
            })
          }
          if (menu.key === 'toggleColumnData') {
            const attrsMap = {}
            newVal.value.forEach((item) => {
              Object.keys(item.attrs).forEach((attrKey) => {
                attrsMap[attrKey] = true
              })
            })
            menu.children = menu.children.filter(item => attrsMap[item.key])
          }
        })
      }
      menuItems.value = menus
    },
  )
  // 表单类型 过滤出menus
  watch(
    () => batchFormType.value,
    (newVal) => {
      menuItems.value = batchTypeMenus(newVal)
    },
  )

  const batchTypeMenus = (type) => {
    let menus = cloneDeep(Menus)
    if (type === 'similar') {
      menus = menus.filter(item => item)
    }
    else {
      menus = menus.filter(item => !item.showType || item.showType !== 'similar')
    }
    return menus
  }

  // 表格列操作菜单
  const menuClick = (item, index) => {
    console.log('item: ', item)
    if (item.domEvent?.target.tagName === 'INPUT')
      return
    const { keyPath } = item
    let key = keyPath[keyPath.length - 1]
    key = key.includes('-else') ? key.replace('-else', '') : key
    let menuItem
    menuItems.value.some((menu) => {
      if (menu.key === key) {
        menuItem = menu
        return true // 找到后立即退出循环
      }
      if (menu.children) {
        menuItem = menu.children.find(child => child.key === key)
        if (menuItem)
          return true // 如果在子菜单中找到，退出循环
      }
      return false
    })

    switch (key) {
      case 'editColumnElement':
        openModal({
          title: t(`dataBatch.${key}`),
          type: key,
          column: cloneDeep(columns[index]),
          width: '100%',
          warpClassName: 'full-modal',
        })
        break
      case 'editColumnName':
        openModal({
          title: t(`dataBatch.${key}`),
          type: key,
          column: { title: columns[index].title, dataIndex: columns[index].dataIndex },
          width: '400px',
        })
        break
      case 'deleteColumn':
        deleteColumn(index)
        break
      case 'copyColumn':
        copyColumn(index)
        break
      case 'insertColumnLeft':
        insertColumn(index, 'left')
        break
      case 'insertColumnRight':
        insertColumn(index, 'right')
        break
      case 'similarAdd':
        addSimilarData(index)
        break
      case 'colFilterConfig':
        openNormalModal(menuItem.label, key, columns[index], '480px')
        break
      case 'filterConfig':
        openNormalModal(menuItem.label, key, columns[index], '480px')
        break
      case 'Replace':
        openNormalModal(menuItem.label, key, columns[index])
        break
      case 'Prefix':
        openNormalModal(menuItem.label, key, columns[index])
        break
      case 'Suffix':
        openNormalModal(menuItem.label, key, columns[index])
        break
      case 'FormatTime':
        openNormalModal(menuItem.label, key, columns[index])
        break
      case 'Regular':
        openNormalModal(menuItem.label, key, columns[index])
        break
      case 'clear':
        clearExpression(columns[index])
        break
      case 'text':
        toggleColumnDataHandle('text', index)
        break
      case 'href':
        toggleColumnDataHandle('href', index)
        break
      case 'src':
        toggleColumnDataHandle('src', index)
        break
      default:
        // message.warning('暂无操作')
        break
    }
  }
  // 打开弹窗
  const openModal = (params) => {
    params.open = true
    batchModalVisible.value = true
    batchModalConfig.value = params
  }
  // 打开小弹窗
  const openNormalModal = (_label, key, col, width = '400px') => {
    openModal({
      title: t(`dataBatch.${key}`),
      type: key,
      column: cloneDeep(col),
      width,
    })
  }
  // 切换显示类型
  const toggleColumnDataHandle = (value_type: string, index: number) => {
    columns[index].value_type = value_type
    const value = columns[index].value
    if (value) {
      value.forEach((item) => {
        item.text = item.attrs[value_type] || ''
      })
    }
    columns[index].value = value
    columnData[index] = value
    columns = columnItemGenerate(columns)
    tableData = tableDataHandle(columns, columnData)
    refresh()
  }
  // 清空表达条件
  const clearExpression = (col) => {
    col.colDataProcessConfig = []
    col.colFilterConfig = []
    col.filterConfig = []
    send2FetchData(columns)
  }
  /**
   * 删除列
   * @param index 当前列索引
   */
  const deleteColumn = (index) => {
    columns.splice(index, 1)
    columnData.splice(index, 1)
    columns = columnItemGenerate(columns)
    tableData = tableDataHandle(columns, columnData)
    refresh()
  }
  /**
   * 复制列
   * @param index 当前列索引
   */
  const copyColumn = (index) => {
    const column = cloneDeep(columns[index])
    const columnDataItem = cloneDeep(columnData[index])
    column.title = `${column.title}_copy`
    column.dataIndex = `${column.dataIndex}_copy`
    column.field = `${column.field}_copy`
    columns.splice(index + 1, 0, column)
    columnData.splice(index + 1, 0, columnDataItem)
    similarTypeHandle(columns, columnData)
    // autoAddColumn() // 自动新增一列
  }
  /**
   * 向指定位置插入列
   * @param index 当前列索引
   * @param insert 插入位置，left: 左边，right: 右边
   */
  const insertColumn = (index: number, insert: 'left' | 'right') => {
    newBatch(index, insert)
    refresh()
  }

  const moreMenuClick = (index: number) => {
    selectedColumnIndex.value = index
    activeColumn.value = cloneDeep(columns[index])
  }
  // checbox 点击
  const checkboxClick = (event, index: number, current: any) => {
    current.checked = event.target.checked
    dataProcessEnable(index, current, event)
  }
  // 条件勾选
  const dataProcessEnable = (index: number, current: any, event) => {
    console.log('event: ', event)
    console.log('current: ', current)
    const column = columns[index]
    console.log('column: ', column)
    const currentProcessConfig = column.colDataProcessConfig.find(item => item.processType === current.key)
    // console.log('currentProcessConfig: ', currentProcessConfig)

    if (current.checked) {
      // 需要弹窗的菜单在没有该条件或者条件为空时需要弹出弹窗
      if ((!currentProcessConfig || currentProcessConfig.parameters.length === 0) && current.modal) {
        openNormalModal(current.label, current.key, column)
        current.checked = false
        return
      }
      // 需要弹窗的菜单如果有当前有处理条件，且处理条件不为空，则更新 isEnable
      if (currentProcessConfig && currentProcessConfig.parameters.length > 0) {
        currentProcessConfig.isEnable = 1
      }
      if (!currentProcessConfig && !current.modal) {
        column.colDataProcessConfig.push({
          processType: current.key,
          isEnable: 1,
          parameters: [],
        })
      }
    }
    else {
      if (currentProcessConfig) {
        // 如果有当前处理条件，则更新 isEnable
        currentProcessConfig.isEnable = 0
      }
      else {
        // 如果没有当前处理条件，则不做处理
        return
      }
    }
    // filterMenus(column)
    // console.log('columns: ', columns)
    // todo 发送抓取对象获取新的数据
    selectedColumnIndex.value = index
    activeColumn.value = cloneDeep(columns[index])
    send2FetchData(columns)
  }
  /**
   * 点击列头
   * @param col 当前列
   */
  const columnClick = (col) => {
    const index = col.columnIndex
    selectedColumnIndex.value = index
    activeColumn.value = cloneDeep(columns[index])
    highLightColumn(index)
  }
  const highLightColumn = (index: number) => {
    if (usePick.isChecking)
      return
    if (isHightLight)
      return
    let colElement = columns[index]
    if (batchFormType.value === 'table') {
      colElement = tableElement
    }
    const path = colElement
    path.checkType = colElement.checkType || VISUALIZATION
    path.matchTypes = []
    path.columnIndex = index + 1 // 从1开始
    const ele = {
      app: colElement.app,
      type: colElement.type,
      version: colElement.version,
      path,
    }
    const eleStr = JSON.stringify(ele)
    isHightLight = true
    useBatchPick.highLight(eleStr, (res) => {
      console.log('highLight res: ', res)
      isHightLight = false
    })
  }

  const resetActiveColumn = () => {
    activeColumn.value = null
    selectedColumnIndex.value = -1
  }

  // grid 配置
  const gridOptions = reactive<VxeGridProps & { columnLength: number, rowLength: number }>({
    stripe: true,
    resizable: true,
    round: true,
    loading: false,
    border: 'none',
    height: 230,
    columns: [],
    data: [],
    columnConfig: {
      isCurrent: true,
    },
    size: 'mini',
    showOverflow: true,
    showHeaderOverflow: 'tooltip',
    showFooterOverflow: true,
    scrollY: {
      enabled: false,
      gt: 0,
    },
    scrollX: {
      enabled: false,
      gt: 0,
    },
    columnLength: 0,
    rowLength: 0,
    loadingConfig: {
      text: '正在抓取...',
    },
  })
  /**
   * 处理列，表格数据，是否开启虚拟滚动
   */
  const handleColumnsAndData = (cols: any[], data: any[]) => {
    if (cols.length > 5) {
      columns = cols.map((col) => {
        return {
          ...col,
          width: 120,
        }
      })
    }
    if (columns.length > 30) {
      gridOptions.scrollX.enabled = true
    }
    if (data.length > 50) {
      gridOptions.scrollY.enabled = true
    }
  }
  /**
   * 加载表格数据
   */
  const loadGridData = () => {
    // console.log('gridOptions: ', gridOptions)
    handleColumnsAndData(columns, tableData)
    // console.log('loadGridData columns: ', columns)
    // console.log('loadGridData tableData: ', tableData)
    gridRef.value
    && gridRef.value.loadColumn(columns).then(() => {
      gridRef.value.loadData(tableData)
      gridOptions.loading = false
      gridOptions.columnLength = columns.length
      gridOptions.rowLength = tableData.length
    })
  }
  /**
   * 刷新表格数据
   */
  const refresh = () => {
    loadGridData()
    resetActiveColumn()
  }

  /**
   *  初始化列配置
   * @param cols 列配置
   */
  const columnsConfig = (cols: any[]) => {
    return cols.map((col) => {
      const filterConfig = col.filterConfig || []
      const colFilterConfig = col.colFilterConfig || []
      const colDataProcessConfig = col.colDataProcessConfig || []
      return {
        ...col,
        filterConfig,
        colFilterConfig,
        colDataProcessConfig,
      }
    })
  }
  /**
   * 表格数据表头数据处理
   */
  const tableHeadGenerate = (cols: any[]) => {
    return cols.map((col, index) => {
      const oldTitle = columns[index]?.title || ''
      const safeIndex = index + 1
      return {
        ...col,
        field: col.field || generateColumnNames(safeIndex),
        title: oldTitle || col.title || generateColumnNames(safeIndex), // 列表头名称
        dataIndex: col.dataIndex || generateColumnNames(safeIndex),
        slots: { header: 'customHeader' },
        showOverflow: 'ellipsis',
        value: col.value, // 列值
      }
    })
  }
  // 表头抓取更新表头
  const tableHeadHandle = (cols: string[]) => {
    if (columns.length === 0) { // 没有抓取过数据，初始化表头
      const thead = cols.map((col) => {
        return { title: col, value: [] }
      })
      columns = tableHeadGenerate(thead)
    }
    columns.forEach((col, index) => {
      col.title = cols[index] || ''
    })
    return columns
  }
  /**
   * 表格数据表格body 数据处理
   */
  const tableBodyGenerate = (cols: any[], rows: any[]) => {
    return rows.map((row, index) => {
      const rowObj = {}
      row.forEach((item, index) => {
        rowObj[cols[index].field] = item
      })
      return {
        key: String(index + 1),
        ...rowObj,
      }
    })
  }
  /**
   * 处理列数据为vxe-grid的格式
   * @param cols 列
   */
  const columnItemGenerate = (cols) => {
    return cols.map((col, index) => {
      const safeIndex = index + 1
      const colName = generateColumnNames(safeIndex) // 默认列名
      return {
        ...col,
        field: colName,
        title: col.title || colName,
        dataIndex: colName,
        slots: { header: 'customHeader' },
        showOverflow: 'ellipsis',
      }
    })
  }

  /**
   * 抓取的数据处理
   * @param data 抓取的数据 { app: string, type: string, version: string, path: { produceType: string, values: any[] } }
   * @param index 第几行数据，用于更新 index 列的数据
   */
  const originDataHandle = (data: BatchElementDataInfo, index?: number, insert?: 'left' | 'right') => {
    const { path, app, type, version, picker_type } = data
    const { isTable, produceType } = path
    batchElementData = { app, path, picker_type, type, version }
    if (isTable) {
      // 表格数据，提示是否抓取单列，还是整个表格
      GlobalModal.confirm({
        title: t('presentation'),
        content: t('dataBatch.tableGetConfirm'),
        okText: t('dataBatch.wholeTable'),
        cancelText: t('dataBatch.singleColumn'),
        onOk: () => {
          // 整个表格
          const { values } = path.tableData
          batchFormType.value = 'table'
          tableElement = { ...path.tableData, app, type, version } // 表格元素
          if (values) {
            tableTypeHandle(values)
          }
        },
        onCancel: () => {
          // 单列, 只会在第一次抓取时出现，columns 不为空时，新增都会以 相似元素抓取的方式处理
          const { values } = path.tableColumnData
          const col = { ...values[0], app, type, version }
          batchFormType.value = 'similar' // 单列抓取，默认以相似元素抓取方式处理
          columns = [col]
          columnData = [values[0].value]
          similarTypeHandle(columns, columnData)
          col.values && delete col.values
          autoAddColumn() // 自动新增一列
        },
        centered: true,
        keyboard: false,
      })
      return
    }
    if (produceType === 'similar') {
      // 相似数据
      const { values } = path
      const col = { ...values[0], app, type, version }
      const colData = values[0].value
      batchFormType.value = 'similar'
      if (columns.length > 0) {
        // 比较新数据和原始数据的tabUrl， 不一致提醒无法夸页面抓取
        const { tabUrl } = columns[0]
        if (tabUrl !== col.tabUrl) {
          message.warning(t('dataBatch.noSupportTwoPage'))
          return
        }
      }
      if (insert === 'left' && index !== undefined) {
        // 在index 的左边插入
        columns.splice(index, 0, col)
        columnData.splice(index, 0, colData)
      }
      if (insert === 'right' && index !== undefined) {
        // 在index 的右边插入
        columns.splice(index + 1, 0, col)
        columnData.splice(index + 1, 0, colData)
      }
      if (insert === undefined && index !== undefined) {
        // 更新 index 的数据,补充相似元素抓取的数据
        columns[index] = col
        columnData[index] = colData
      }
      if (insert === undefined && index === undefined) {
        // 新增一列，新增抓取
        columns.push(col)
        columnData.push(colData)
      }
      similarTypeHandle(columns, columnData)
      autoAddColumn()
    }
  }
  /**
   * tableData数据
   */
  const tableDataHandle = (cols, colsData: any[]) => {
    const tableDataTemp: any[] = []
    for (let i = 0; i < colsData.length; i++) {
      const colData = colsData[i]
      const col = cols[i]
      colData.forEach((item, index) => {
        tableDataTemp[index] = tableDataTemp[index] ? tableDataTemp[index] : { key: String(index + 1) }
        tableDataTemp[index][col.field] = item.text
      })
    }
    return tableDataTemp
  }

  /**
   * 相似抓取数据处理
   * @param cols 列
   * @param colsData 列的数据，原始数据的 values
   */
  const similarTypeHandle = (cols, colsData: any[]) => {
    columns = columnItemGenerate(cols)
    columns = columnsConfig(columns)
    tableData = tableDataHandle(columns, colsData)
    refresh()
  }

  /**
   * table 抓取数据处理
   * @param values
   */
  const tableTypeHandle = (values: any[]) => {
    console.log('tableTypeHandle: ', values)
    const tbody = []
    values.forEach((col) => {
      col.value.forEach((item, index2) => {
        tbody[index2] = tbody[index2] || []
        tbody[index2].push(item)
      })
    })
    columns = tableHeadGenerate(values)
    columns = columnsConfig(columns)
    tableData = tableBodyGenerate(columns, tbody)
    refresh()
  }

  /**
   * 自动新增一列
   */
  const autoAddColumn = () => {
    console.trace('autoAddColumn')
    let retryCount = 0
    const maxRetries = 10 // Maximum number of retries

    if (retryCount >= maxRetries) {
      console.warn('Max retries reached. Stopping autoAddColumn.')
      return
    }
    setTimeout(() => {
      if (gridOptions.loading) {
        retryCount++
        autoAddColumn()
      }
      else {
        retryCount = 0 // Reset retry count on success
        newBatch()
      }
    }, 200) // 延时200毫秒，等待数据处理完成
  }

  /**
   * 新增抓取
   */
  const newBatch = (index?: number, insert?: 'left' | 'right') => {
    if (usePick.isChecking)
      return
    const batchType = batchFormType.value === 'similar' ? 'similar' : ''
    gridOptions.loading = true
    useBatchPick.startBatchPick('batch', { path: { batchType } }, (res) => {
      console.log('newBatch result: ', res)
      gridOptions.loading = false
      if (res.success) {
        const { type } = res.data
        if (type === 'web') {
          originDataHandle(res.data, index, insert)
        }
        else {
          message.warning(t('dataBatch.noSupportNotWeb'))
        }
      }
    })
  }
  /**
   * 表头抓取
   */
  const batchTableHead = () => {
    if (usePick.isChecking)
      return
    useBatchPick.startBatchPick('batch', { path: { batchType: 'head' } }, (res) => {
      if (res.success) {
        const { type, path } = res.data
        console.log('batchTableHead res: ', res)
        if (type === 'web') {
          columns = tableHeadHandle(path)
          columns = columnsConfig(columns)
          refresh()
        }
        else {
          message.warning(t('dataBatch.noSupportNotWeb'))
        }
      }
    })
  }
  /**
   * 补充相似元素
   * @param index 列索引
   */
  const addSimilarData = (index: number) => {
    if (usePick.isChecking)
      return
    const elements = columns[index]
    if (elements && 'xpath' in elements) {
      const path = JSON.parse(JSON.stringify(elements))
      path.checkType = VISUALIZATION
      path.matchTypes = []
      path.batchType = 'similarAdd'
      'value' in path && delete path.value
      const originElements = {
        app: elements.app,
        type: elements.type,
        version: elements.version,
        path,
      }
      useBatchPick.startBatchPick('batch', originElements, (res) => {
        if (res.success) {
          const { type } = res.data
          if (type === 'web') {
            originDataHandle(res.data, index)
          }
          else {
            message.warning(t('dataBatch.noSupportNotWeb'))
          }
        }
      })
    }
    else {
      message.warning(t('dataBatch.pleaseSelectColumn'))
    }
  }
  /**
   * 清空
   */
  const clear = () => {
    columnData = []
    tableData = []
    columns = []
    selectedColumnIndex.value = -1
    batchFormType.value = ''
    activeColumn.value = null
    tableElement = {}
    // batchObject = null
    batchElementData = null
    checkData.value = false
    refresh()
  }
  // 弹窗确认
  const handleModalOk = (params) => {
    // console.log('params: ', params);
    const data = params.column
    // console.log('handleModalOk data: ', data)
    batchModalVisible.value = false
    const { dataIndex } = data
    columns.forEach((item) => {
      if (item.dataIndex === dataIndex) {
        Object.assign(item, data)
        selectedColumnIndex.value = -1
        activeColumn.value = null
      }
    })
    // 除了编辑列名，其他情况都发送请求
    if (params.type !== 'editColumnName') {
      send2FetchData(columns)
    }
    else {
      loadGridData()
    }
  }
  // 编辑表格元素
  const editTableElement = () => {
    openModal({
      title: t(`dataBatch.editColumnElement`),
      type: 'editColumnElement',
      width: '100%',
      warpClassName: 'full-modal',
      column: tableElement,
    })
  }

  /**
   * 保存元素
   */
  const save = () => {
    formRef.value.validate().then((valid) => {
      if (valid) {
        if (!columns.length) {
          message.warning(t('dataBatch.batchFirst'))
          return
        }
        // 保存抓取的元素到元素库
        elementHandle()
      }
    })
  }
  const elementHandle = () => {
    const robotId = getUrlQueryField('robotId')
    const _name = formState.name
    let elementDataObj
    // const thead = columns.map((item) => {
    //   // 表头
    //   return item.title
    // })
    console.log('columns: ', columns)
    if (batchFormType.value === 'similar') {
      elementDataObj = {
        ...batchElementData,
        path: {
          checkType: columns[0]?.checkType || VISUALIZATION,
          matchTypes: [],
          produceType: batchFormType.value,
          values: columns.map((item) => {
            return removeColumnUselessKey(item)
          }),
        },
      }
    }
    else {
      elementDataObj = {
        ...batchElementData,
        path: {
          checkType: tableElement.checkType || VISUALIZATION,
          matchTypes: [],
          ...tableElement,
          // thead,
          produceType: batchFormType.value,
        },
      }
      elementDataObj.path = removeColumnUselessKey(elementDataObj.path) // 去掉不需要的属性
      elementDataObj.path.values = columns.map((item) => {
        return removeColumnUselessKey(item)
      })
    }
    console.log('elementDataObj: ', elementDataObj)

    if (isEdit) {
      updateElement({
        robotId,
        element: {
          commonSubType: 'batch',
          id: batchObject.id,
          name: _name,
          elementData: JSON.stringify(elementDataObj),
        },
      }).then((res) => {
        if (res.code === '000000') {
          saveDone(_name, batchObject.id, robotId)
        }
      })
    }
    else {
      addElement({
        type: 'common',
        robotId,
        groupName: batchElementData.app,
        element: {
          commonSubType: 'batch',
          name: _name,
          icon: '',
          elementData: JSON.stringify(elementDataObj),
        },
      }).then((res) => {
        if (res.code === '000000') {
          saveDone(_name, res.data.elementId, robotId)
        }
      })
    }
  }
  const saveDone = (name: string, elementId: string, robotId: string) => {
    const noEmit = getUrlQueryField('noEmit')
    windowManager.emitTo({
      target: WINDOW_NAME.MAIN,
      type: 'save',
      from: WINDOW_NAME.BATCH,
      data: {
        name,
        elementId,
        robotId,
        noEmit,
      },
    })
    windowManager.closeWindow(WINDOW_NAME.BATCH)
  }
  // remove column useless key
  const removeColumnUselessKey = (column: any) => {
    const newItem = { ...column }
    Object.keys(newItem).forEach((key) => {
      if (ColumnsKeys.includes(key)) {
        delete newItem[key]
      }
    })
    return newItem
  }

  // 取消
  const cancel = () => {
    closeDataBatch(false)
  }

  // 关闭窗口
  function closeDataBatch(ask: boolean = true, data: any = {}) {
    if (useBatchPick.isPicking) {
      message.warning(t('dataBatch.dontCloseAtRuning'))
      return
    }
    function close() {
      windowManager.emitTo({
        target: WINDOW_NAME.MAIN,
        type: 'close',
        from: WINDOW_NAME.BATCH,
        data,
      })
      windowManager.closeWindow(WINDOW_NAME.BATCH)
    }
    if (!ask) {
      close()
    }
    else {
      GlobalModal.confirm({
        getContainer: () => document.querySelector('#dataBatch'),
        title: t('presentation'),
        content: t('dataBatch.windowCloseConfirm'),
        onOk() {
          close()
        },
        centered: true,
        keyboard: false,
      })
    }
  }
  /**
   * 打开源页面, 获取数据
   */
  function openSourcePage() {
    getElementData(batchObject, true)
  }

  // 初始化
  const hookInit = () => {
    http.resolveReadyPromise()
    isEdit = getUrlQueryField('isEdit') === 'true'
    const robotId = getUrlQueryField('robotId')
    if (isEdit) {
      // 编辑元素
      const elementId = getUrlQueryField('elementId')
      getElementDetail({
        robotId,
        elementId,
      }).then((res) => {
        batchObject = res.data
        getElementData(res.data)
      })
    }
    else {
      // 新增元素
      newBatch()
    }
    //  获取所有元素列表
    getElementsAll({
      robotId,
      elementType: 'common',
    }).then((res) => {
      let allElements = []
      // 将 res.data数组内item 的elements 数组扁平化
      res.data.forEach((item) => {
        allElements = allElements.concat(item.elements)
      })
      if (!isEdit) {
        const allElementsNames = allElements.map(item => item.name)
        formState.name = generateSheetName(allElementsNames, locale)
      }
    })
  }

  // 初始化编辑数据
  function getElementData(data: { name: string, elementData: string }, openSourcePage: boolean = false) {
    console.log('编辑的元素 data: ', data)
    const { name, elementData } = data
    formState.name = name
    gridOptions.loading = true
    const element = elementData ? JSON.parse(elementData) : {}
    console.log('element: ', element)
    batchElementData = element
    if (openSourcePage) {
      element.path.openSourcePage = true
    }
    const timer = setTimeout(() => {
      gridOptions.loading = false
      checkData.value = true
      useBatchPick.finishCheck()
    }, 10 * 1000) // 10秒后自动关闭
    useBatchPick.getBatchData('batch', JSON.stringify(element), (res) => {
      if (res.success) {
        const { data } = res
        if (data) {
          const { produceType } = data
          batchFormType.value = produceType
          if (produceType === 'table') {
            const { values } = data
            tableElement = { ...element, ...data }
            tableElement.path && delete tableElement.path
            if (values) {
              tableTypeHandle(values)
            }
          }
          else {
            const { values } = data
            columns = values.map(item => item)
            columnData = values.map(item => item.value)
            similarTypeHandle(columns, columnData)
          }
        }
        else {
          checkData.value = true
        }
        clearTimeout(timer)
      }
      else {
        checkData.value = true
        gridOptions.loading = false
        clearTimeout(timer)
      }
    })
  }

  function send2FetchData(cols) {
    console.log('send2FetchData cols: ', cols)
    gridOptions.loading = true
    // console.log('send2FetchData batchFormType: ', batchFormType.value)
    if (batchFormType.value === 'similar') {
      batchElementData.path = {
        produceType: 'similar',
        checkType: cols[0].checkType || VISUALIZATION,
        matchTypes: [],
        values: cols.map((item) => {
          return removeColumnUselessKey(item)
        }),
      }
    }
    else {
      batchElementData.path = {
        ...tableElement,
        produceType: 'table',
        checkType: cols[0]?.checkType || VISUALIZATION,
        matchTypes: [],
        values: cols.map((item) => {
          return removeColumnUselessKey(item)
        }),
      }
    }
    console.log('send2FetchData batchElementData: ', batchElementData)
    useBatchPick.getBatchData('batch', JSON.stringify(batchElementData), (res) => {
      console.log('getBatchData res: ', res)
      const { data } = res
      if (data) {
        const { produceType } = data
        if (produceType === 'table') {
          const { values } = data
          if (values) {
            tableTypeHandle(values)
          }
        }
        else {
          const { values } = data
          columns = values.map(item => item)
          columnData = values.map(item => item.value)
          similarTypeHandle(columns, columnData)
        }
      }
      loadGridData()
    })
  }

  return {
    formState,
    columns,
    tableData,
    menuItems,
    selectedColumnIndex,
    gridOptions,
    gridRef,
    formRef,
    rules,
    batchFormType,
    activeColumn,
    batchModalRef,
    checkData,
    menuClick,
    columnClick,
    loadGridData,
    save,
    cancel,
    newBatch,
    batchTableHead,
    clear,
    addSimilarData,
    handleModalOk,
    editTableElement,
    hookInit,
    closeDataBatch,
    openSourcePage,
    moreMenuClick,
    dataProcessEnable,
    checkboxClick,
    batchModalVisible,
    batchModalConfig,
  }
}
