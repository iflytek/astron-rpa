import GlobalModal from '@/components/GlobalModal/index.ts'
/**
 * 刷新弹窗
 */
export function refreshModal() {
  GlobalModal.confirm({
    title: '提示',
    content: '检测到资源已更新，是否刷新页面？',
    onOk: () => {
      window.location.reload()
    },
    // onCancel: () => {
    //   refreshPlugin();
    // }
    centered: true,
    keyboard: false,
  })
}
