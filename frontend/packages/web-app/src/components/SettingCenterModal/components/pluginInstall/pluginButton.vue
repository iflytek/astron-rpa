<script lang="tsx">
import { Button, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import type { PropType } from 'vue'
import { defineComponent } from 'vue'

import type { PLUGIN_ITEM } from '@/constants/plugin'

export default defineComponent({
  title: 'PluginButton',
  props: {
    item: {
      type: Object as PropType<PLUGIN_ITEM>,
      required: true,
    },
  },
  emits: {
    click: () => true,
  },
  setup(props, { emit }) {
    const { item } = props
    const { i18next } = useTranslation()

    const getBtnText = () => {
      if (item.isInstall) {
        return item.isNewest ? 'reinstall' : 'pluginUpdate' // 重新安装、插件更新
      }

      // if (item.type === '2345') {
      //   return 'installationTutorial' // 安装教程
      // }

      // if (item.type === 'driver') {
      //   return 'driverInstallation' // 驱动安装
      // }

      return 'intelligentInstallation' // 智能安装
    }

    const getBtnType = () => {
      if (!item.isInstall || !item.isNewest) {
        return 'primary'
      }

      return 'default'
    }

    return () => {
      const isZh = i18next.language === 'zh-CN'
      const btnText = i18next.t(getBtnText())

      const buttonComponent = (
        <Button
          class={[
            'plugIn-content_button',
            `plugIn-content_button__${i18next.language}`,
          ]}
          loading={item.loading}
          type={getBtnType()}
          onClick={() => emit('click')}
        >
          {isZh ? btnText : <div class="text-ellipsis">{btnText}</div>}
        </Button>
      )

      if (isZh)
        return buttonComponent

      return <Tooltip title={btnText}>{buttonComponent}</Tooltip>
    }
  },
})
</script>

<style lang="scss">
.plugIn-content_button {
  font-size: $font-size-sm;

  &__en-US {
    width: 80px;
    padding-left: 10px;
    padding-right: 10px;
  }

  .text-ellipsis {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
