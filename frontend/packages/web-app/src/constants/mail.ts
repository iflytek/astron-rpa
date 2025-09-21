export const EMAIL_OPTIONS = [
  {
    label: '163',
    value: '163Email',
  },
  {
    label: '126',
    value: '126Email',
  },
  {
    label: 'QQ',
    value: 'qqEmail',
  },
  {
    label: '其他邮箱',
    value: 'customEmail',
  },
]

// 映射
export const EMAIL_OPTIONS_MAP = {
  // `qq`、`163`、`126`、`iflytek`、advance`
  'customEmail': 'advance',
  'advance': 'advance',
  '126Email': '126',
  '126': '126',
  '163Email': '163',
  '163': '163',
  'qqEmail': 'qq',
  'qq': 'qq',
  'iflytekEmail': 'iflytek',
  'iflytek': 'iflytek',
}

export const PROTOCAL_OPTIONS = [
  {
    label: 'IMAP',
    value: 'IMAP',
  },
  {
    label: 'POP3',
    value: 'POP3',
  },
]
