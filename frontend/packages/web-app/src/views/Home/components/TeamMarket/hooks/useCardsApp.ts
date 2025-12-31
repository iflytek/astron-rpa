import { findIndex } from 'lodash-es'
import { reactive, ref } from 'vue'

import { getAllClassification, getAppCards, marketUserList } from '@/api/market'
import { fromIcon } from '@/components/PublishComponents/utils'
import { useCardsTools } from '@/views/Home/components/TeamMarket/hooks/useCardsTools'
import type { resOption } from '@/views/Home/types'

import { useRobotUpdate } from './useRobotUpdate'

/**
 * 使用卡片应用的自定义Hook
 * @returns {object} 返回包含首页列表引用、卡片配置和获取团队成员方法的对象
 */
export function useCardsApp() {
  // 首页列表组件的引用
  const homePageListRef = ref(null)
  function refreshHomeTable() {
    if (homePageListRef.value) {
      homePageListRef.value?.fetchTableData()
    }
  }
  // 获取应用更新ID的解构赋值
  const { getInitUpdateIds } = useRobotUpdate('app', homePageListRef)
  /**
   * 获取卡片数据
   * @param {object} params - 请求参数，包含marketId等信息
   * @returns {Promise} 返回一个Promise，解析为包含records和total的对象
   */
  function getCardsData(params) {
    return new Promise((resolve) => {
      if (params.marketId) {
        getAppCards(params).then((res: resOption) => {
          const { data } = res
          if (data) {
            const { total, records } = data
            // 获取初始化更新ID
            getInitUpdateIds(records)
            resolve({
              records: records.map(item => ({
                ...item,
                icon: fromIcon(item.url || item.iconUrl).icon,
                color: fromIcon(item.url || item.iconUrl).color,
              })),
              total,
            })
          }
        })
      }
    })
  }

  // 获取卡片工具中的表单列表
  const { formList } = useCardsTools()
  // 响应式卡片配置对象
  const cardsOption = reactive({
    type: 'cards', // 卡片类型
    refresh: false,
    getData: getCardsData, // 获取数据的方法
    formList, // 表单列表
    params: { // 绑定的表单配置的数据
      marketId: '', // 市场ID
      appName: '',
      creatorId: undefined, // 创建者ID
      category: undefined,
      sortKey: 'createTime', // 排序键
    },
  })
  /**
   * 根据团队获取成员列表
   * @param {string} marketId - 市场ID
   */
  function getMembersByTeam(marketId) {
    marketUserList({
      marketId,
      pageNo: 1,
      pageSize: 10000,
    }).then((res: resOption) => {
      const { data } = res
      if (data) {
        const { records } = data
        // 构建所有者列表，包含姓名和电话
        const ownerList = records.map((i) => {
          return {
            name: `${i.realName || '--'}(${i.phone || '--'})`,
            userId: i.creatorId,
          }
        })
        // 找到绑定creatorId的表单项并更新其选项
        const current = cardsOption.formList[findIndex(cardsOption.formList, { bind: 'creatorId' })]
        current.options = ownerList
      }
    })
  }

  async function getAppCategory() {
    const res = await getAllClassification()
    const current = cardsOption.formList[findIndex(cardsOption.formList, { bind: 'category' })]
    current.options = res.data || []
  }

  // 返回所需的引用和方法
  return {
    homePageListRef,
    refreshHomeTable,
    cardsOption,
    getMembersByTeam,
    getAppCategory,
  }
}
