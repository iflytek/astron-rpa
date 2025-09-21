import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { Segmented, Space } from 'ant-design-vue'
import { reactive, ref } from 'vue'

const meta = {
  title: 'Antdv/Segmented',
  component: Segmented,
} satisfies Meta<typeof Segmented>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    type: 'primary',
  },
  render: args => ({
    components: { Segmented, Space },
    setup() {
      const data = reactive(['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'])
      const value = ref(data[0])

      return { args, data, value }
    },
    template: `
      <Space wrap>
        <Segmented v-model:value="value" :options="data" />
      </Space>
    `,
  }),
}
