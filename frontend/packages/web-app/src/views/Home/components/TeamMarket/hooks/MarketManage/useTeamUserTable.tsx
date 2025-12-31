import { Button, message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { storeToRefs } from 'pinia'
import { h, inject, reactive, ref, watch } from 'vue'

import { dissolveTeamMarket, inviteMarketUser, leaveTeamMarket, marketUserList, removeUserRole, setUserRole } from '@/api/market'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { TEAMMARKETS } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { clipboardManager } from '@/platform'
import { useMarketStore } from '@/stores/useMarketStore'
import type { Fun } from '@/types/common'
import { MARKET_TYPE_PUBLIC, MARKET_USER_ADMIN, MARKET_USER_OWNER, USER_TYPES } from '@/views/Home/components/TeamMarket/config/market'
import FireTeam from '@/views/Home/components/TeamMarket/MarketManage/FireTeam.vue'
import GiveOwner from '@/views/Home/components/TeamMarket/MarketManage/GiveOwner.vue'
import InviteUser from '@/views/Home/components/TeamMarket/MarketManage/InviteUser.vue'
import RoleDropdown from '@/views/Home/components/TeamMarket/MarketManage/RoleDropdown.vue'

const INIT_SCROLLY = window.innerHeight - 480

export function useTeamUserTable() {
  const { setOnlyUser } = inject('isOnlyUser') as { setOnlyUser: Fun }
  const homeTableRef = ref(null)
  const marketStore = useMarketStore()
  const { activeMarket } = storeToRefs(marketStore)
  const { t } = useTranslation()

  const getUserList = (params) => {
    return new Promise((resolve) => {
      marketUserList({
        marketId: activeMarket.value.marketId,
        ...params,
      }).then(({ data }) => {
        // data && resolve(data)
        if (data) {
          setOnlyUser(data.records.length === 1)
          resolve(data)
        }
      })
    })
  }

  const removeUser = ({ creatorId }) => {
    GlobalModal.confirm({
      title: t('market.removeUserConfirm'),
      okType: 'danger',
      onOk: () => {
        removeUserRole({ creatorId, marketId: activeMarket.value.marketId }).then((res) => {
          const { data } = res
          if (data) {
            message.success(t('market.removeUserSuccess'))
            refreshTableData()
          }
          else {
            message.error(t('market.removeUserFail'))
          }
        })
      },
      onCancel() {
        console.log('Cancel')
      },
      centered: true,
      keyboard: false,
    })
  }

  const changeUserType = (itemData, userType) => {
    const { creatorId } = itemData
    const user = USER_TYPES.find(item => item.key === userType)?.name
    GlobalModal.confirm({
      title: t('market.setUserRoleConfirm', { role: user }),
      onOk: () => {
        setUserRole({
          userType,
          marketId: activeMarket.value.marketId,
          creatorId,
        }).then(({ data }) => {
          if (data) {
            message.success(t('market.setUserRoleSuccess'))
            refreshTableData()
          }
        })
      },
      onCancel() {
        console.log('Cancel')
      },
      centered: true,
      keyboard: false,
    })
  }

  // 邀请用户
  const inviteUser = () => {
    const inviteType = ref('link') // phone 组织架构 link 邀请链接
    const inviteUsers = ref([])
    const inviteLink = ref('')
    try {
      const m = GlobalModal.confirm({
        title: t('market.inviteMember'),
        class: 'invite-user-modal',
        icon: null,
        width: 540,
        content: h(
          <InviteUser
            marketId={activeMarket.value.marketId}
            onInviteTypeChange={(type: string) => {
              inviteType.value = type
              m.update({
                okText: inviteType.value === 'link' ? '复制链接' : '确定',
              })
            }}
            onChange={values => inviteUsers.value = values}
            onLinkChange={(link: string) => {
              inviteLink.value = link
              m.update({
                okButtonProps: { loading: false, disabled: inviteType.value === 'link' ? !inviteLink.value : inviteUsers.value.length <= 0 },
              })
            }}
          />,
        ),
        okText: inviteType.value === 'link' ? '复制链接' : '确定',
        okButtonProps: { loading: false, disabled: inviteType.value === 'link' ? !inviteLink.value : inviteUsers.value.length <= 0 },
        onOk: () => {
          return new Promise((resolve, reject) => {
            if (inviteType.value === 'link') {
              clipboardManager.writeClipboardText(inviteLink.value)
              message.success('复制成功')
              reject(new Error('复制成功'))
              return
            }
            if (inviteUsers.value.length <= 0) {
              const error = t('market.noInviteMember')
              message.warn(error)
              reject(new Error(error))
              return
            }

            inviteMarketUser({ marketId: activeMarket.value.marketId, userInfoList: inviteUsers.value })
              .then((res) => {
                if (res.data) {
                  message.success(t('market.inviteMemberSuccess'))
                }
                else {
                  message.error(t('market.inviteMemberFail'))
                }
                resolve(true)
              })
          })
        },
        onCancel() {
          console.log('Cancel')
        },
        centered: true,
        keyboard: false,
      })
    }
    catch (e) {
      console.log(e)
    }
  }

  // 离开
  const leaveTeam = () => {
    GlobalModal.confirm({
      title: t('market.leaveTeam'),
      content: t('market.leaveTeamConfirm', { marketName: activeMarket.value.marketName }),
      onOk: () => {
        leaveTeamMarket({ newOwner: '', marketId: activeMarket.value.marketId })
          .then(async (res) => {
            if (res.data) {
              message.success(t('common.operationSuccess'))
              await marketStore.refreshTeamList()
              await useRoutePush({ name: TEAMMARKETS })
              homeTableRef.value.value.localOption.params.marketId = activeMarket.value.marketId
            }
          })
          .catch((e) => {
            if (e.message.includes('刷新页面')) {
              marketStore.refreshTeamList(activeMarket.value.marketId, true)
            }
          })
      },
      centered: true,
      keyboard: false,
    })
  }

  // 移交所有权
  const giveOwner = () => {
    const newManager = ref('')
    GlobalModal.confirm({
      title: t('market.transferOwnership'),
      content: (
        <GiveOwner
          marketId={activeMarket.value.marketId}
          onChange={(value) => {
            console.log(newManager)
            newManager.value = value
          }}
        />
      ),
      onOk: () => {
        if (!newManager.value) {
          message.error(t('market.selectTransferUser'))
          return
        }
        leaveTeamMarket({ newOwner: newManager.value, marketId: activeMarket.value.marketId })
          .then(async (res) => {
            if (res.data) {
              message.success(t('common.operationSuccess'))
              await marketStore.refreshTeamList()
              await useRoutePush({ name: TEAMMARKETS })
              homeTableRef.value.value.localOption.params.marketId = activeMarket.value.marketId
            }
          })
          .catch((e) => {
            if (e.message.includes('刷新页面')) {
              marketStore.refreshTeamList(activeMarket.value.marketId, true)
            }
          })
      },
      centered: true,
      keyboard: false,
    })
  }

  // 解散团队
  const fireTeam = () => {
    const teamName = ref('')
    GlobalModal.confirm({
      title: t('market.dissolveTeam'),
      content: <FireTeam marketName={activeMarket.value.marketName} onChange={value => teamName.value = value} />,
      onOk: () => {
        if (!teamName.value) {
          message.error(t('market.enterDissolveTeamName'))
          return
        }
        dissolveTeamMarket({ marketName: teamName.value, marketId: activeMarket.value.marketId })
          .then(async (res) => {
            if (res.data) {
              message.success(t('common.operationSuccess'))
              await marketStore.refreshTeamList()
              await useRoutePush({ name: TEAMMARKETS })
              homeTableRef.value.value.localOption.params.marketId = activeMarket.value.marketId
            }
          })
      },
      centered: true,
      keyboard: false,
    })
  }

  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    getData: getUserList,
    formList: [
      {
        componentType: 'input',
        bind: 'userName',
        placeholder: 'common.enterUserName',
      },
      {
        componentType: 'input',
        bind: 'realName',
        placeholder: 'common.enterRealName',
      },
    ],
    buttonList: [
      {
        label: 'market.inviteMember',
        action: 'design_cloud_pj_create',
        clickFn: () => inviteUser(),
        type: 'primary',
        hidden: ![MARKET_USER_OWNER, MARKET_USER_ADMIN].includes(activeMarket.value.userType),
      },
    ],
    tableProps: {
      columns: [
        {
          title: 'common.userName',
          dataIndex: 'userName',
          key: 'userName',
          ellipsis: true,
        },
        {
          title: 'common.realName',
          dataIndex: 'realName',
          key: 'realName',
          ellipsis: true,
        },
        {
          title: 'common.email',
          dataIndex: 'email',
          key: 'email',
          ellipsis: true,
        },
        {
          title: 'common.phone',
          dataIndex: 'phone',
          key: 'phone',
          ellipsis: true,
        },
        {
          title: 'market.joinTime',
          dataIndex: 'createTime',
          key: 'createTime',
          ellipsis: true,
          sorter: true,
        },
        {
          title: 'operate',
          dataIndex: 'oper',
          key: 'oper',
          width: 150,
          customRender: ({ record }) => {
            return (
              <div class="custom-box">
                <RoleDropdown userType={record.userType} onChange={userType => changeUserType(record, userType)} />
                <Button
                  type="link"
                  size="small"
                  disabled={record.userType === MARKET_USER_OWNER || (activeMarket.value.marketType === MARKET_TYPE_PUBLIC && record.userType === MARKET_USER_ADMIN)}
                  onClick={() => removeUser(record)}
                >
                  {t('market.removeUser')}
                </Button>
              </div>
            )
          },
        },
      ],
      rowKey: 'id',
      scroll: { y: INIT_SCROLLY },
    },
    params: {
      userName: '',
      realName: '',
    },
  })

  const refreshTableData = () => {
    homeTableRef.value && homeTableRef.value.fetchTableData()
  }

  watch(() => activeMarket.value?.marketId, (newVal) => {
    if (newVal) {
      refreshTableData()
    }
  }, {
    immediate: true,
  })

  watch(() => activeMarket.value?.userType, (newVal) => {
    if (newVal) {
      refreshTableData()
    }
  })

  return {
    giveOwner,
    leaveTeam,
    fireTeam,
    homeTableRef,
    tableOption,
    refreshTableData,
  }
}
