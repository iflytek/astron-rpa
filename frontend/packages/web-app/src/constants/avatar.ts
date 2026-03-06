import i18next from '@/plugins/i18next'

export interface AvatarItem {
  name?: string
  icon: string
}

export const ROBOT_AVATAR_LIST: AvatarItem[] = [
  { name: 'avatar.robot', icon: 'avatar-robot' },
  { name: 'avatar.finance', icon: 'avatar-finance' },
  { name: 'avatar.education', icon: 'avatar-education' },
  { name: 'avatar.game', icon: 'avatar-gaming' },
  { name: 'avatar.e-commerce', icon: 'avatar-ecommerce' },
  { name: 'avatar.live-broadcast', icon: 'avatar-live-streaming' },
  { name: 'avatar.telecommunications', icon: 'avatar-telecom' },
  { name: 'avatar.government', icon: 'avatar-government' },
  { name: 'avatar.architecture', icon: 'avatar-construction' },
  { name: 'avatar.tobacco', icon: 'avatar-tobacco' },
  { name: 'avatar.operation', icon: 'avatar-operations' },
  { name: 'avatar.human-resources', icon: 'avatar-hr' },
  { name: 'avatar.urban-services', icon: 'avatar-city-service' },
  { name: 'avatar.car', icon: 'avatar-automotive' },
  { name: 'avatar.new-energy', icon: 'avatar-new-energy' },
  { name: 'avatar.manufacturing', icon: 'avatar-manufacturing' },
]

export const ROBOT_DEFAULT_ICON = 'avatar-internet-1'

export const COMPONENT_AVATAR_LIST: AvatarItem[] = [
  { icon: 'avatar-comp-1' },
  { icon: 'avatar-comp-2' },
  { icon: 'avatar-comp-3' },
  { icon: 'avatar-comp-4' },
  { icon: 'avatar-comp-5' },
  { icon: 'avatar-comp-6' },
  { icon: 'avatar-comp-7' },
  { icon: 'avatar-comp-8' },
  { icon: 'avatar-comp-9' },
  { icon: 'avatar-comp-10' },
  { icon: 'avatar-comp-11' },
  { icon: 'avatar-comp-12' },
  { icon: 'avatar-comp-13' },
  { icon: 'avatar-comp-14' },
  { icon: 'avatar-comp-15' },
  { icon: 'avatar-comp-16' },
  { icon: 'avatar-comp-17' },
  { icon: 'avatar-comp-18' },
]

export const COMPONENT_DEFAULT_ICON = COMPONENT_AVATAR_LIST[0].icon

export const COLOR_LIST = ['#726FFF', '#1677FF', '#13C2C2', '#2FCB64', '#A0D911', '#FADB14', '#FA8C16', '#FA541C', '#EB2F96']

export const DEFAULT_COLOR = COLOR_LIST[0]

export const NEW_ROBOT_AVATAR_LIST = [
  {
    type: 'internet',
    typeName: i18next.t('avatarType.internet'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-internet-${index + 1}`),
  },

  {
    type: 'office-supplies',
    typeName: i18next.t('avatarType.office-supplies'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-office-supplies-${index + 1}`),
  },

  {
    type: 'medical',
    typeName: i18next.t('avatarType.medical'),
    list: Array.from({ length: 87 }, (_, index) => `avatar-medical-${index + 1}`),
  },

  {
    type: 'business',
    typeName: i18next.t('avatarType.business'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-business-${index + 1}`),
  },

  {
    type: 'navigation-map',
    typeName: i18next.t('avatarType.navigation-map'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-navigation-map-${index + 1}`),
  },

  {
    type: 'industry-construction',
    typeName: i18next.t('avatarType.industry-construction'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-industry-construction-${index + 1}`),
  },

  {
    type: 'education',
    typeName: i18next.t('avatarType.education'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-education-${index + 1}`),
  },

  {
    type: 'digital-electronics',
    typeName: i18next.t('avatarType.digital-electronics'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-digital-electronics-${index + 1}`),
  },

  {
    type: 'technology',
    typeName: i18next.t('avatarType.technology'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-technology-${index + 1}`),
  },

  {
    type: 'design-development',
    typeName: i18next.t('avatarType.design-development'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-design-development-${index + 1}`),
  },

  {
    type: 'finance',
    typeName: i18next.t('avatarType.finance'),
    list: Array.from({ length: 90 }, (_, index) => `avatar-finance-${index + 1}`),
  },
]
