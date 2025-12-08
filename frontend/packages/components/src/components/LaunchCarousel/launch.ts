export interface IllustrationItem {
  img: string
  text: string
  desc: string
}

export const illustrationList: IllustrationItem[][] = [
  [
    {
      img: 'designer-illustration-1',
      text: '创建自动化机器人',
      desc: '从左侧拖拽原子能力到中间编辑区',
    },
    {
      img: 'designer-illustration-2',
      text: '创建自动化机器人',
      desc: '使用元素拾取器捕获一个界面控件',
    },
    {
      img: 'designer-illustration-3',
      text: '创建自动化机器人',
      desc: '编辑对应原子能力',
    },
    {
      img: 'designer-illustration-4',
      text: '创建自动化机器人',
      desc: '点击运行查看机器人完整执行过程',
    },
  ],
  [
    {
      img: 'actuator-illustration-1',
      text: '通过执行器新建计划任务',
      desc: '选择单个或多个机器人',
    },
    {
      img: 'actuator-illustration-2',
      text: '通过执行器新建计划任务',
      desc: '选择触发方式',
    },
    {
      img: 'actuator-illustration-3',
      text: '通过执行器新建计划任务',
      desc: '执行器调用机器人运行',
    },
    {
      img: 'actuator-illustration-4',
      text: '通过执行器新建计划任务',
      desc: '执行记录页面查看执行记录：完整日志和录屏',
    },
  ],
  [
    {
      img: 'market-illustration-1',
      text: '团队机器人共享',
      desc: '支持发布机器人至指定团队市场，实现共享',
    },
    {
      img: 'market-illustration-2',
      text: '获取共享机器人',
      desc: '可获取进行二次开发，也可获取直接运行',
    },
  ],
]
