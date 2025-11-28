<script lang="ts" setup>
import CvPickBtn from '@/views/Arrange/components/cvPick/CvPickBtn.vue'
import CvUploadBtn from '@/views/Arrange/components/cvPick/CvUploadBtn.vue'

import ManageHeader from '../ManageHeader.vue'
</script>

<template>
  <ManageHeader element-type="cv">
    <template #btns>
      <CvPickBtn class="mr-2" />
      <CvUploadBtn />
    </template>
  </ManageHeader>
</template>
