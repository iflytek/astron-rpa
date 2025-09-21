/**
 *  市场数据
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import { getTeams } from '@/api/market'
import { APPLICATION } from '@/constants/menu'

const TEAM_KEY = 'teamMarket'
const APPLICATION_KEY = 'application'

export const useMarketStore = defineStore('market', () => {
  const route = useRoute()
  const markets = ref([
    {
      key: TEAM_KEY,
      name: 'all',
      children: [],
      route: '',
      active: true,
    },
    {
      key: APPLICATION_KEY,
      name: 'market.myApplication',
      route: APPLICATION,
      children: [],
      active: false,
    },
  ])

  // 当前选中的市场数据
  const activeMarket = ref(null)

  // 获取团队市场数据
  const getTeamList = (id: string = '', isEdit: boolean = false) => {
    return new Promise((resolve, reject) => {
      getTeams().then((res) => {
        setMarketData(TEAM_KEY, res.data || [])
        if (route.name === APPLICATION) {
          setCurrentMarketItem(APPLICATION_KEY)
          return
        }
        let marketId = res.data[0]?.marketId || ''
        if (id && res.data.find(i => i.marketId === id)) {
          marketId = id
        }
        !isEdit && setCurrentMarketItem(marketId)
        isEdit && activeMarket.value?.marketId && setCurrentMarketItem(activeMarket.value.marketId)
        resolve(true)
      }).catch((err) => {
        console.log('getTeamList', err)
        reject(err)
      })
    })
  }

  // 设置市场数据
  const setMarketData = (marketKey: string, data: any[]) => {
    markets.value.find(i => i.key === marketKey).children = data
  }

  // 设置当前选中的市场数据
  const setCurrentMarketItem = (marketId: string) => {
    if (!marketId) {
      activeMarket.value = null
      return
    }
    markets.value = markets.value.map((item) => {
      item.active = (item.key === marketId || item.children.some(i => i.marketId === marketId)) || false
      return item
    })
    const marketsItem = markets.value.find(item => item.active)
    activeMarket.value = marketsItem.children.length > 0 ? (marketsItem.children.find(item => item.marketId === marketId) || null) : null
  }

  const reset = () => {
    markets.value = markets.value.map((item) => {
      item.children = []
      return item
    })
    markets.value[0].active = true
    activeMarket.value = null
  }

  const refreshTeamList = (marketId?: string, isEdit: boolean = false) => {
    return getTeamList(marketId, isEdit)
  }

  return {
    markets,
    activeMarket,
    setCurrentMarketItem,
    refreshTeamList,
    reset,
  }
})
