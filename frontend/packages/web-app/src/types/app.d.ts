declare namespace RPA {
  type Theme = 'light' | 'dark' | 'auto'

  type IMailFlag = 'qq' | '163' | '126' | 'iflytek' | 'advance'

  interface IMailItem {
    id: number
    emailAccount: string
    emailProtocol: string
    emailService: IMailFlag
    port: string
    enableSSL: boolean
    emailServiceAddress: string
    authorizationCode: string
  }
}
