import { Button, message } from 'ant-design-vue'
import { debounce } from 'lodash-es'
import { ref, reactive } from 'vue'

import { getInviteUser, getTransferUser, generateInviteLink, resetInviteLink, } from '@/api/market'
import { MARKET_USER_COMMON } from '@/views/Home/components/TeamMarket/config/market'
import type { resOption } from '@/views/Home/types'
import RoleDropdown from '@/views/Home/components/TeamMarket/MarketManage/RoleDropdown.vue'
import { VUE_APP_AUTH } from '@/constants'

export function usePhoneInvite(marketId: string, type: string = 'invite', emit?: any) {
  const userList = ref([])
  const selectIds = ref([])
  const tempSelectIds = ref([])
  const allSelectUsers = ref([])
  const defaultUserType = ref(MARKET_USER_COMMON)

  const userListByPhone = debounce((phone) => {
    if (!phone) {
      userList.value = []
      return
    }

    if (Object.is(Number(phone), Number.NaN) || phone.length > 11) {
      message.destroy()
      message.error('请输入正确的手机号')
      userList.value = []
      return
    }

    const func = type === 'invite' ? getInviteUser : getTransferUser
    func({ phone, marketId }).then((res: resOption) => {
      const { data } = res
      if (Array.isArray(data)) {
        userList.value = data.map((item) => {
          if (!item.userType)
            item.userType = MARKET_USER_COMMON
          return item
        })
      }
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
    addIds.forEach(id => {
      const user = allData.find(i => i.creatorId === id)
      if (user) {
        if(allSelectUsers.value.find(i => i.creatorId === id)) {
          allSelectUsers.value = allSelectUsers.value.filter(item => item.creatorId !== id)
        }
        allSelectUsers.value.unshift({...user, userType: defaultUserType.value})
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
    allSelectUsers.value.find(i=>i.creatorId === record.creatorId).userType = userType
    triggerChange()
  }

  const removeUser = (record) => {
    allSelectUsers.value = allSelectUsers.value.filter(i => i.creatorId !== record.creatorId)
    selectIds.value =  allSelectUsers.value.map(i => i.creatorId)
    triggerChange()
  }

  const inviteUsersTableColumns = [
    {
      dataIndex: 'realName',
      key: 'realName',
      ellipsis: true,
      customRender: ({ record }) => {
        return <span>{record.realName}({record.phone})</span>
      }
    },
    {
      dataIndex: 'userType',
      key: 'userType',
      ellipsis: true,
      customRender: ({ record }) => {
        return (
          <RoleDropdown userType={record.userType} onChange={userType => changeUserType(record, userType)} />
        )
      }
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
  const invitData = ref({
    inviteKey: "",
    expireTime: "",
    overNumLimit: 0,
    expireType: "24H",
  })
  const expireTypes = ref([
    { label: '4小时后过期', value: '4H' },
    { label: '24小时后过期', value: '24H' },
    { label: '7天后过期', value: '7D' },
    { label: '30天后过期', value: '30D' },
  ])

  const formState = reactive({
    inviteLink: '',
    expireType: '24H',
  })

  const retInviteLink = (data) => {
    invitData.value = data
    formState.inviteLink = data.overNumLimit === 1 ? '' : `${VUE_APP_AUTH}?inviteKey=${data.inviteKey}`
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
