import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { Button, Space } from 'ant-design-vue'

const meta = {
  title: 'Antdv/Button',
  component: Button,
} satisfies Meta<typeof Button>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    type: 'primary',
  },
  render: args => ({
    components: { Button, Space },
    setup() {
      return { args }
    },
    template: `
      <Space wrap>
        <Button type="primary">Primary Button</Button>
        <Button>Default Button</Button>
        <Button type="dashed">Dashed Button</Button>
        <Button type="text">Text Button</Button>
        <Button type="link">Link Button</Button>
      </Space>
    `,
  }),
}
