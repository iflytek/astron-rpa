<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { useTranslation } from 'i18next-vue'

import { CreateTeamMarketModal } from '@/components/CreateTeamMarketModal'

const openTeam = () => NiceModal.show(CreateTeamMarketModal)
const { t } = useTranslation()
</script>

<template>
  <section class="w-full h-full flex justify-center items-center">
    <a-empty>
      <span slot="description">
        {{ t('market.createMarketTipPrefix') }}
        <span class="text-primary cursor-pointer" @click="openTeam">
          {{ t('market.click') }}
        </span>
        {{ t('market.createMarketTipSuffix') }}
      </span>
    </a-empty>
  </section>
</template>
