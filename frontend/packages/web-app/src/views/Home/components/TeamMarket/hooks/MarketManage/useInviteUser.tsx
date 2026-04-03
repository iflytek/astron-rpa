import { Button, message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { debounce } from 'lodash-es'
import { storeToRefs } from 'pinia'
import { reactive, ref } from 'vue'

import { generateInviteLink, getInviteUser, getTransferUser, resetInviteLink } from '@/api/market'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { MARKET_USER_COMMON } from '@/views/Home/components/TeamMarket/config/market'
import RoleDropdown from '@/views/Home/components/TeamMarket/MarketManage/RoleDropdown.vue'

export function usePhoneInvite(marketId: string, type: string = 'invite', emit?: any) {
  const { t } = useTranslation()
  const userList = ref([])
  const selectIds = ref([])
  const tempSelectIds = ref([])
  const allSelectUsers = ref([])
  const defaultUserType = ref(MARKET_USER_COMMON)

  const userListByPhone = debounce((keyword) => {
    if (!keyword) {
      userList.value = []
      return
    }

    if (type !== 'invite' && (Object.is(Number(keyword), Number.NaN) || keyword.length > 11)) {
      message.destroy()
      message.error(t('common.invalidPhoneNumber'))
      userList.value = []
      return
    }

    const func = type === 'invite' ? getInviteUser : getTransferUser
    const params = type === 'invite' ? { keyword, marketId } : { phone: keyword, marketId }
    func(params).then((data) => {
      if (Array.isArray(data)) {
        userList.value = data.map((item) => {
          if (!item.userType)
            item.userType = MARKET_USER_COMMON
          return item
        })
      }
    }).catch(() => {
      userList.value = []
    })
  }, 200)

  const keyDownChange = (e) => {
    const { keyCode } = e
    if (keyCode === 13 && userList.value.length === 1) {
      const id = userList.value[0].creatorId
      if (!selectIds.value.includes(id)) {
        selectIds.value.push(id)
        triggerChange()
      }
    }
  }

  const selectData = (val) => {
    selectIds.value = val
    triggerChange()
  }

  const triggerChange = () => {
    const selectUsers = userList.value.filter(i => selectIds.value.includes(i.creatorId))
    const addIds = selectIds.value.filter(id => !tempSelectIds.value.includes(id))
    const delIds = tempSelectIds.value.filter(id => !selectIds.value.includes(id))
    const allData = allSelectUsers.value.concat(selectUsers)
    addIds.forEach((id) => {
      const user = allData.find(i => i.creatorId === id)
      if (user) {
        if (allSelectUsers.value.find(i => i.creatorId === id)) {
          allSelectUsers.value = allSelectUsers.value.filter(item => item.creatorId !== id)
        }
        allSelectUsers.value.unshift({ ...user, userType: defaultUserType.value })
      }
    })

    allSelectUsers.value = allSelectUsers.value.filter(item => !delIds.includes(item.creatorId))

    tempSelectIds.value = selectIds.value

    const users = allSelectUsers.value.map((item) => {
      return {
        userType: item.userType,
        creatorId: item.creatorId,
        realName: item.realName,
        phone: item.phone,
      }
    })
    emit && emit('change', users)
  }
  const changeDefaultUserType = (userType) => {
    defaultUserType.value = userType
  }
  const clearUserList = () => {
    userList.value = []
    selectIds.value = []
    tempSelectIds.value = []
  }

  const resetPhoneInviteArr = () => {
    selectIds.value = []
    triggerChange()
  }

  const changeUserType = (record, userType) => {
    allSelectUsers.value.find(i => i.creatorId === record.creatorId).userType = userType
    triggerChange()
  }

  const removeUser = (record) => {
    allSelectUsers.value = allSelectUsers.value.filter(i => i.creatorId !== record.creatorId)
    triggerChange()
  }

  const inviteUsersTableColumns = [
    {
      dataIndex: 'realName',
      key: 'realName',
      ellipsis: true,
      customRender: ({ record }) => {
        return (
          <span>
            {record.realName}
            (
            {record.phone}
            )
          </span>
        )
      },
    },
    {
      dataIndex: 'userType',
      key: 'userType',
      ellipsis: true,
      customRender: ({ record }) => {
        return (
          <RoleDropdown userType={record.userType} onChange={userType => changeUserType(record, userType)} />
        )
      },
    },
    {
      dataIndex: 'oper',
      key: 'oper',
      width: 50,
      customRender: ({ record }) => {
        return (
          <div class="custom-box">
            <Button
              type="link"
              size="small"
              onClick={() => removeUser(record)}
            >
              移除
            </Button>
          </div>
        )
      },
    },
  ]

  return {
    userList,
    userListByPhone,
    inviteUsersTableColumns,
    selectIds,
    allSelectUsers,
    defaultUserType,
    clearUserList,
    keyDownChange,
    selectData,
    changeDefaultUserType,
    resetPhoneInviteArr,
  }
}

export function useLinkInvite(marketId: string, emit?: any) {
  const appStore = useAppConfigStore()
  const { appInfo } = storeToRefs(appStore)
  const { t } = useTranslation()
  const invitData = ref({
    inviteKey: '',
    expireTime: '',
    overNumLimit: 0,
    expireType: '24H',
  })
  const expireTypes = ref([
    { label: t('market.expireAfter4Hours'), value: '4H' },
    { label: t('market.expireAfter24Hours'), value: '24H' },
    { label: t('market.expireAfter7Days'), value: '7D' },
    { label: t('market.expireAfter30Days'), value: '30D' },
  ])

  const formState = reactive({
    inviteLink: '',
    expireType: '24H',
  })

  const retInviteLink = (data) => {
    invitData.value = data
    formState.inviteLink = data.overNumLimit === 1 ? '' : `${appInfo.value.remotePath}login/#/invite?inviteKey=${data.inviteKey}`
    formState.expireType = data.expireType || '24H'
    emit && emit('linkChange', formState.inviteLink)
  }

  const generateLink = async () => {
    const res = await generateInviteLink({ marketId, expireType: formState.expireType })
    retInviteLink(res.data)
  }

  const resetLink = async () => {
    const res = await resetInviteLink({ marketId, expireType: formState.expireType })
    retInviteLink(res.data)
  }

  generateLink()

  return {
    invitData,
    expireTypes,
    formState,
    resetLink,
  }
}
