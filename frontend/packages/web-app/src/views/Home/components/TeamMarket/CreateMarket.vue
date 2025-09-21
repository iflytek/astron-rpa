<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { CreateTeamMarketModal } from '@/components/CreateTeamMarketModal'

const openTeam = () => NiceModal.show(CreateTeamMarketModal)
</script>

<template>
  <section class="w-full h-full flex justify-center items-center">
    <a-empty>
      <span slot="description">
        您还未创建或加入任何团队市场，
        <span class="text-primary cursor-pointer" @click="openTeam">
          点击
        </span>
        创建团队市场
      </span>
    </a-empty>
  </section>
</template>
