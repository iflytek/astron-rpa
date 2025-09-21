import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { Button, Modal } from 'ant-design-vue'
import { ref } from 'vue'

const meta = {
  title: 'Antdv/Modal',
  component: Modal,
} satisfies Meta<typeof Modal>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => ({
    components: { Button, Modal },
    setup() {
      const open = ref<boolean>(false)

      const showModal = () => {
        open.value = true
      }

      const handleOk = (e: MouseEvent) => {
        console.log(e)
        open.value = false
      }
      return { open, showModal, handleOk }
    },
    template: `
      <div>
        <Button type="primary" @click="showModal">Open Modal</Button>
        <Modal v-model:open="open" title="Basic Modal" @ok="handleOk">
          <p>Some contents...</p>
          <p>Some contents...</p>
          <p>Some contents...</p>
        </Modal>
      </div>
    `,
  }),
}
