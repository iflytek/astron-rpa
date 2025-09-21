<script lang="tsx">
import { useElementSize } from '@vueuse/core'
import { Empty, Pagination, Table } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { isEmpty } from 'lodash-es'
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'

// import type { TableOption } from '@/types/normalTable'
import useTable from './hooks/useTable'

const PAGE_SIZE_OPTIONS = ['15', '30', '50', '100']
const DEFAULT_PAGE = 1
// 暂时设为常量，后续可以考虑使用从 antv tokens 中获取 需考虑不同table的默认高度可能不同
const TABLE_HEADER_HEIGHT = 47 // 表头高度
const TABLE_CELL_HEIGHT = 49 // 表单项高度

function getItemsOnPage(total: number, pageSize: number, page: number) {
  // 确保参数有效
  if (total <= 0 || pageSize <= 0 || page <= 0) {
    return 0
  }

  // 计算总页数
  const totalPages = Math.ceil(total / pageSize)

  // 如果请求的页码超过总页数，返回0
  if (page > totalPages) {
    return 0
  }

  // 如果是最后一页，计算实际项数
  if (page === totalPages) {
    return total - (pageSize * (totalPages - 1))
  }

  // 其他页都是满页
  return pageSize
}

export default {
  name: 'NormalTable',
  props: {
    option: {
      // type: Object as () => TableOption,
      // default(): TableOption {
      //   return {
      //     getData: async () => ({ records: [], total: 0 }),
      //     tableProps: { columns: [] },
      //   }
      // },
      type: Object,
      default() {
        return {}
      },
    },
  },
  setup(props, { expose, slots }) {
    const { t } = useTranslation()
    /**
     * 如何让 table 的 scroll 高度自适应？
     * 1. 使用 position: absolute 让 table 脱离文档流
     * 2. 使用 useElementSize 获取 table 所在容器的 height
     * 3. 如果 table 没有占满容器，则不设置 table 的 scroll
     * 4. 否则，设置 table 的 scroll 高度为容器高度减去 47px
     */
    const tableElement = useTemplateRef<HTMLTableElement>('table')
    const tableSize = useElementSize(tableElement)

    const { option } = reactive({ ...props })
    const { renderHeaderForm, renderHeaderButton } = useTable()
    const localOption = computed(() => option)
    const pageData = ref(option?.pageParams || { pageNoName: 'pageNo', pageSizeName: 'pageSize' })
    const pageOption = ref({ // 分页配置
      total: 0,
      current: 1,
      pageNum: 1,
      pageSize: Number((PAGE_SIZE_OPTIONS)[0]),
      pageSizeOptions: PAGE_SIZE_OPTIONS,
      size: 'small' as const,
      showSizeChanger: true,
      showQuickJumper: true,
      ...(option?.pageConfig || {}),
    })
    const orderData = ref(option?.orderParams || { orderName: 'sortBy', orderStatus: 'sortType' }) // 排序字段
    const immediate = ref(option?.immediate === false ? option.immediate : true) // 是否立即执行
    const isPage = ref(option?.page === false ? option.page : true) // 是否开启分页，默认分页
    const loading = ref(false) // 开启loading
    const tableData = ref([]) // 表格数据
    const formOption = reactive({ // 表单配置
      formList: option?.formList || [],
      params: option?.params || {},
      searchFn: () => {
        if (isPage.value) {
          pageOption.value.current = Number(DEFAULT_PAGE)
          pageOption.value.pageNum = Number(DEFAULT_PAGE)
          localOption.value.params[pageData.value.pageNoName] = Number(DEFAULT_PAGE)
        }
        fetchTableData()
      },
    })

    const buttonOption = reactive({ // 按钮配置
      buttonList: option?.buttonList || [],
    })

    const tableColumns = computed(() => {
      return option.tableProps?.columns.map(item => ({
        ...item,
        title: t(item.title),
      })) || []
    })

    function fetchTableData() {
      loading.value = true
      if (isPage.value) {
        localOption.value.params[pageData.value.pageSizeName] = pageOption.value.pageSize
        localOption.value.params[pageData.value.pageNoName] = pageOption.value.pageNum
      }
      localOption.value
        .getData({ ...localOption.value.params })
        .then((res) => {
          tableData.value = res.records
          pageOption.value.total = res.total
        })
        .catch(() => {
          tableData.value = []
          pageOption.value.total = 0
        })
        .finally(() => {
          loading.value = false
        })
    }
    function onPageChange(page: number) {
      pageOption.value.pageNum = page
      pageOption.value.current = page

      fetchTableData()
    }
    function onShowSizeChange(_, size) {
      pageOption.value.pageSize = size
    }
    // 分页、排序、筛选
    function tableChange(pagination, filters, sorter) {
      const { field, order } = sorter // sorter有可能为空
      const ORDER_OPTION = {
        ascend: 'asc',
        descend: 'desc',
      }
      localOption.value.params[orderData.value.orderName] = field || '' // checkNum
      localOption.value.params[orderData.value.orderStatus] = ORDER_OPTION[order] || '' // ascend

      fetchTableData()
    }
    function renderTable() { // 默认支持table
      const page = pageOption.value.current
      const pageSize = pageOption.value.pageSize
      const total = pageOption.value.total

      // 计算 table 的最大高度
      const currentCellLength = getItemsOnPage(total, pageSize, page)
      const maxHeight = currentCellLength * (option.tableCellHeight || TABLE_CELL_HEIGHT) + TABLE_HEADER_HEIGHT
      // 判断 table 容器是否占满
      const isFull = tableSize.height.value < maxHeight

      return (
        <Table
          key={isFull ? 'full' : 'notFull'}
          {...localOption.value.tableProps}
          columns={tableColumns.value}
          scroll={{ y: isFull ? tableSize.height.value - TABLE_HEADER_HEIGHT : undefined }}
          class="custom-table absolute w-full"
          loading={loading.value}
          dataSource={tableData.value}
          pagination={false}
          v-slots={{
            emptyText: () => <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={localOption.value.emptyText ?? undefined} />,
          }}
          onChange={tableChange}
          size={option.size || 'small'}
        />
      )
    }
    function renderPagination() {
      return (
        <div class="nTable-pagination flex items-center justify-between">
          <div>
            {t('common.totalData', { total: pageOption.value.total })}
          </div>
          <Pagination
            onChange={onPageChange}
            onShowSizeChange={onShowSizeChange}
            {...pageOption.value}
          />
        </div>
      )
    }

    onMounted(() => {
      if (immediate.value && option.params) {
        fetchTableData()
      }
    })

    expose({
      tableData,
      fetchTableData,
      localOption,
    })

    return () => {
      const hasForm = !isEmpty(option.formList)
      const hasBtns = !isEmpty(option.buttonList)

      return (
        <div class="wrapper h-full">
          <div class="nTable h-full flex flex-col gap-4">
            {/* 头部 */}
            {
              (hasBtns || hasForm) && (
                <div class={['nTable-header', { 'flex-row-reverse': option.formListAlign === 'right' || option.buttonListAlign === 'left' }]}>
                  {/* 左侧form */}
                  {hasForm && renderHeaderForm(formOption)}
                  {/* 右侧button */}
                  {hasBtns && renderHeaderButton(buttonOption)}
                </div>
              )
            }
            {/* 主体 */}
            <div class="flex-1 relative" ref="table">
              {slots.default?.({ loading: loading.value, tableData: tableData.value, height: tableSize.height.value }) || renderTable()}
            </div>
            {/* 底部 */}
            {isPage.value && renderPagination()}
          </div>
        </div>
      )
    }
  },
}
</script>

<style lang="scss" scoped>
@import './index.scss';

// .custom-table :deep(.ant-table-body) {
//   /* 隐藏滚动条但保留滚动功能 */
//   scrollbar-width: none; /* Firefox */
//   -ms-overflow-style: none; /* IE and Edge */

//   &::-webkit-scrollbar {
//     display: none; /* Chrome, Safari and Opera */
//   }
// }

:deep(.ant-table-row-level-1) {
  background-color: var(--color-fill-secondary);
}
</style>
