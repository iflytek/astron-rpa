import i18next from '@/plugins/i18next'

export interface IllustrationItem {
  img: string
  text: string
  desc: string
}

export const illustrationList: IllustrationItem[][] = [
  [
    {
      img: 'designer-illustration-1',
      text: i18next.t('launch.designer.text'),
      desc: i18next.t('launch.designer.desc1'),
    },
    {
      img: 'designer-illustration-2',
      text: i18next.t('launch.designer.text'),
      desc: i18next.t('launch.designer.desc2'),
    },
    {
      img: 'designer-illustration-3',
      text: i18next.t('launch.designer.text'),
      desc: i18next.t('launch.designer.desc3'),
    },
    {
      img: 'designer-illustration-4',
      text: i18next.t('launch.designer.text'),
      desc: i18next.t('launch.designer.desc4'),
    },
  ],
  [
    {
      img: 'actuator-illustration-1',
      text: i18next.t('launch.actuator.text'),
      desc: i18next.t('launch.actuator.desc1'),
    },
    {
      img: 'actuator-illustration-2',
      text: i18next.t('launch.actuator.text'),
      desc: i18next.t('launch.actuator.desc2'),
    },
    {
      img: 'actuator-illustration-3',
      text: i18next.t('launch.actuator.text'),
      desc: i18next.t('launch.actuator.desc3'),
    },
    {
      img: 'actuator-illustration-4',
      text: i18next.t('launch.actuator.text'),
      desc: i18next.t('launch.actuator.desc4'),
    },
  ],
  [
    {
      img: 'market-illustration-1',
      text: i18next.t('launch.market.text1'),
      desc: i18next.t('launch.market.desc1'),
    },
    {
      img: 'market-illustration-2',
      text: i18next.t('launch.market.text2'),
      desc: i18next.t('launch.market.desc2'),
    },
  ],
]
