<script lang="tsx">
import { Button, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import type { PropType } from 'vue'
import { computed, defineComponent } from 'vue'

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
    const { i18next } = useTranslation()

    const getBtnText = computed(() => {
      if (props.item.isInstall) {
        return props.item.isNewest ? 'reinstall' : 'pluginUpdate' // 重新安装、插件更新
      }
      return 'intelligentInstallation' // 智能安装
    })

    const getBtnType = computed(() => {
      if (!props.item.isInstall || !props.item.isNewest) {
        return 'primary'
      }

      return 'default'
    })

    return () => {
      const isZh = i18next.language === 'zh-CN'
      const btnText = i18next.t(getBtnText.value)

      const buttonComponent = (
        <Button
          class={[
            'plugIn-content_button',
            `plugIn-content_button__${i18next.language}`,
          ]}
          loading={props.item.loading}
          type={getBtnType.value}
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
