<script setup lang="ts">
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtImage,
  ChainOfThoughtSearchResult,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '@/ai-components/chain-of-thought'
import { Image } from '@/ai-components/image'
import { DotIcon, ImageIcon, SearchIcon } from 'lucide-vue-next'
import { isEmpty } from 'lodash-es'

import type { Step } from './utils'
import { getHostname, getLogoSrc } from './utils'

interface Props {
  steps: Step[]
  isStreaming?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: true,
})
</script>

<template>
  <div class="border-border border-[1px] p-4 rounded-xl">
    <slot v-if="$slots.empty && isEmpty(props.steps)" name="empty" />

    <ChainOfThought v-else default-open>
      <ChainOfThoughtHeader>
        {{ props.isStreaming ? '操作屏幕中' : '已完成' }}
      </ChainOfThoughtHeader>
      <ChainOfThoughtContent>
        <!-- Empty / loading state -->
        <template v-if="props.steps.length === 0 && isStreaming">
          <ChainOfThoughtStep
            label="正在连接…"
            status="active"
          >
            <template #icon>
              <DotIcon class="size-4" />
            </template>
          </ChainOfThoughtStep>
        </template>

        <!-- Render each step dynamically -->
        <template
          v-for="step in steps"
          :key="step.id"
        >
          <!-- Search step -->
          <ChainOfThoughtStep
            v-if="step.type === 'search'"
            :label="step.label"
            :status="step.status"
          >
            <template #icon>
              <SearchIcon class="size-4" />
            </template>
            <ChainOfThoughtSearchResults v-if="step.data?.searchResults && step.data.searchResults.length > 0">
              <ChainOfThoughtSearchResult
                v-for="result in step.data.searchResults"
                :key="result.url"
              >
                <img
                  alt=""
                  class="size-4"
                  :height="16"
                  :src="getLogoSrc(result.url)"
                  :width="16"
                >
                {{ getHostname(result.url) }}
              </ChainOfThoughtSearchResult>
            </ChainOfThoughtSearchResults>
          </ChainOfThoughtStep>

          <!-- Image step -->
          <ChainOfThoughtStep
            v-else-if="step.type === 'image'"
            :label="step.label"
            :status="step.status"
          >
            <template #icon>
              <ImageIcon class="size-4" />
            </template>
            <ChainOfThoughtImage
              v-if="step.data?.imageBase64"
              :caption="step.data.imageCaption"
            >
              <Image
                :alt="step.data.imageCaption ?? ''"
                class="aspect-square h-[150px] border"
                :base64="step.data.imageBase64 ?? ''"
                :media-type="step.data.imageMediaType ?? 'image/jpeg'"
              />
            </ChainOfThoughtImage>
          </ChainOfThoughtStep>

          <!-- Thinking step (reasoning_content) -->
          <ChainOfThoughtStep
            v-else-if="step.type === 'thinking'"
            :label="step.label"
            :status="step.status"
          >
            <template #icon>
              <DotIcon class="size-4" />
            </template>
            <p
              v-if="step.data?.content"
              class="text-muted-foreground text-xs whitespace-pre-wrap"
            >
              {{ step.data.content }}
            </p>
          </ChainOfThoughtStep>

          <!-- Text step (regular assistant content) -->
          <ChainOfThoughtStep
            v-else
            :label="step.label"
            :status="step.status"
          >
            <template #icon>
              <DotIcon class="size-4" />
            </template>
          </ChainOfThoughtStep>
        </template>
      </ChainOfThoughtContent>
    </ChainOfThought>
  </div>
</template>
