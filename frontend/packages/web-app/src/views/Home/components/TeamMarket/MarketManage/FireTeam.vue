<script setup lang="ts">
import { Input } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

const { marketName } = defineProps({
  marketName: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['change'])
const { t } = useTranslation()

const fireTeamName = ref('')

function changefireTeamName() {
  emit && emit('change', fireTeamName.value)
}
</script>

<template>
  <div class="modal-form">
    <div class="modal-form">
      <div class="modal-form-title">
        {{ t('market.confirmDisbandTeam', { marketName }) }}
      </div>
      <Input
        v-model:value="fireTeamName"
        class="modal-form-input"
        :placeholder="t('market.enterTeamNameConfirm')"
        :max-length="20"
        @change="changefireTeamName"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>
