import { nanoid } from 'nanoid'

export const limitFormsNum = 50 // 限制自定义对话框用户拖拽的最大表单数

export const defaultValueConfig = {
  formType: {
    type: 'INPUT_VARIABLE',
  },
  key: 'defaultValue',
  title: '默认值',
  placeholder: '请输入默认值',
  default: '',
  value: [
    {
      type: 'other',
      value: '',
    },
  ],
  rpa: 'special',
}
export const pwdDefaultValueConfig = {
  formType: {
    type: 'DEFAULTPASSWORD',
  },
  key: 'defaultValue',
  title: '默认值',
  placeholder: '请输入默认值',
  default: '',
  limitLength: [4, 16],
  value: '',
}
export const requiredConfig = {
  formType: {
    type: 'CHECKBOX',
  },
  title: '设置该表单控件为必填',
  options: [
    {
      label: '是',
      value: true,
    },
    {
      label: '否',
      value: false,
    },
  ],
  default: false,
  required: false,
  value: false,
}
export const timeFormatConfig = {
  formType: {
    type: 'SELECT',
  },
  key: 'time_format_select',
  title: '时间格式',
  options: [
    {
      label: '年-月-日',
      value: 'YYYY-MM-DD',
    },
    {
      label: '年-月-日 时:分',
      value: 'YYYY-MM-DD HH:mm',
    },
    {
      label: '年-月-日 时:分:秒',
      value: 'YYYY-MM-DD HH:mm:ss',
    },
    {
      label: '年/月/日',
      value: 'YYYY/MM/DD',
    },
    {
      label: '年/月/日 时:分',
      value: 'YYYY/MM/DD HH:mm',
    },
    {
      label: '年/月/日 时:分:秒',
      value: 'YYYY/MM/DD HH:mm:ss',
    },
  ],
  default: 'YYYY-MM-DD',
  required: false,
  value: 'YYYY-MM-DD',
}
export const timeDefaultValueConfig = {
  formType: {
    type: 'DEFAULTDATEPICKER',
    params: {
      format: 'YYYY-MM-DD',
    },
  },
  key: 'default_time',
  title: '默认时间',
  default: '',
  value: '',
}
export const fileTypeConfig = {
  formType: {
    type: 'RADIO',
  },
  key: 'file_type',
  title: '选择类型',
  options: [
    {
      label: '文件',
      value: 'file',
    },
    {
      label: '文件夹',
      value: 'folder',
    },
  ],
  default: 'file',
  value: 'file',
}
export const fileFilterConfig = {
  formType: {
    type: 'SELECT',
  },
  key: 'file_filter_select',
  title: '文件类型',
  options: [
    {
      label: '所有文件',
      value: '*',
    },
    {
      label: 'Excel文件',
      value: '.xls,.xlsx',
    },
    {
      label: 'Word文件',
      value: '.doc,.docx',
    },
    {
      label: '文本文件',
      value: '.txt',
    },
    {
      label: '图像文件',
      value: '.png,.jpg,.bmp',
    },
    {
      label: 'PPT文件',
      value: '.ppt,.pptx',
    },
    {
      label: '压缩文件',
      value: '.zip,.rar',
    },
  ],
  default: '*',
  value: '*',
}
export const defaultFilePathConfig = {
  formType: {
    type: 'INPUT_VARIABLE_PYTHON_FILE',
    params: {
      file_type: 'folder',
    },
  },
  key: 'default_file_path',
  title: '默认文件夹',
  default: '',
  value: [
    {
      type: 'other',
      value: '',
    },
  ],
  rpa: 'special',
}
export const optionsConfig = {
  formType: {
    type: 'OPTIONSLIST',
  },
  key: 'options',
  title: '选项',
  default: [],
  required: true,
  value: [{
    rId: nanoid(),
    value: {
      rpa: 'special',
      value: [
        {
          type: 'other',
          value: '选项1',
        },
      ],
    },
  }],
}
export const defaultSingleSelectConfig = {
  formType: {
    type: 'SELECT',
  },
  key: 'default_option_single_select',
  title: '默认值',
  options: [
    {
      label: '选项1',
      value: nanoid(),
    },
  ],
  allowReverse: false,
  default: '',
  value: '',
}
export const defaultMultiSelectConfig = {
  formType: {
    type: 'SELECT',
    params: {
      multiple: true,
    },
  },
  key: 'default_option_multi_select',
  title: '默认值',
  options: [
    {
      label: '选项1',
      value: nanoid(),
    },
  ],
  allowReverse: false,
  default: [],
  value: [],
}
export const directionConfig = {
  formType: {
    type: 'RADIO',
  },
  key: 'direction',
  title: '排列方向',
  options: [
    {
      label: '横向排列',
      value: 'horizontal',
    },
    {
      label: '纵向排列',
      value: 'vertical',
    },
  ],
  default: 'horizontal',
  value: 'horizontal',
}
export const fontFamilyConfig = {
  formType: {
    type: 'SELECT',
  },
  key: 'fontFamily',
  title: '字体',
  options: [
    {
      label: '微软雅黑',
      value: 'msyh',
    },
    {
      label: '宋体',
      value: 'simsun',
    },
    {
      label: '黑体',
      value: 'simhei',
    },
    {
      label: '仿宋',
      value: 'simfang',
    },
    {
      label: 'Times New Roman',
      value: 'times',
    },
    {
      label: '楷体',
      value: 'KaiTi',
    },
    {
      label: '隶书',
      value: 'LiShu',
    },
    {
      label: '新宋体',
      value: 'NSimSun',
    },
    {
      label: '幼圆',
      value: 'YouYuan',
    },
    {
      label: 'Arial',
      value: 'Arial',
    },
    {
      label: 'Microsoft JhengHei',
      value: 'MicrosoftJhengHei',
    },
    // {
    //   label: 'Microsoft YaHei UI',
    //   value: 'Microsoft YaHei UI',
    // },
    {
      label: 'Calibri',
      value: 'Calibri',
    },
  ],
  default: 'msyh',
  required: false,
  value: 'msyh',
}
export const fontSizeConfig = {
  formType: {
    type: 'FONTSIZENUMBER',
  },
  key: 'fontSize',
  title: '字号',
  min: 12,
  max: 72,
  step: 2,
  default: 12,
  required: true,
  value: 12,
}
export const fontStyleConfig = {
  formType: {
    type: 'CHECKBOXGROUP',
  },
  key: 'fontStyle',
  title: '字体属性',
  options: [
    {
      label: '加粗',
      value: 'bold',
    },
    {
      label: '斜体',
      value: 'italic',
    },
    {
      label: '下划线',
      value: 'underline',
    },
  ],
  default: [],
  value: [],
}
export const textContentConfig = {
  formType: {
    type: 'INPUT',
  },
  key: 'textContent',
  title: '内容',
  placeholder: '请输入文本描述',
  default: '文本描述',
  value: [
    {
      type: 'other',
      value: '文本描述',
    },
  ],
  rpa: 'special',
  required: true,
}
export const fontFamilyMap = {
  msyh: 'font-family: "msyh", "微软雅黑", sans-serif', // 微软雅黑
  simsun: 'font-family: "simsun", "宋体", sans-serif;', // 宋体
  simhei: 'font-family: "simhei", "黑体", sans-serif;', // 黑体
  simfang: 'font-family: "simfang", "仿宋", sans-serif;', // 仿宋
  times: 'font-family: "times", "Times New Roman", sans-serif;', // Times New Roman
  KaiTi: 'font-family: "KaiTi", "楷体", sans-serif;', // 楷体
  LiShu: 'font-family: "LiShu", "隶书", sans-serif;', // 隶书
  NSimSun: 'font-family: "NSimSun", "新宋体", sans-serif;', // 新宋体
  YouYuan: 'font-family: "YouYuan", "幼圆", sans-serif;', // 幼圆
  Arial: 'font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;', // Arial
  MicrosoftJhengHei: 'font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;', // Microsoft JhengHei
  Calibri: 'Calibri, "Helvetica Neue", Helvetica, Arial, sans-serif', // Calibri
}
export const fontStyleMap = {
  bold: 'font-weight: bold',
  italic: 'font-style: italic',
  underline: 'text-decoration: underline',
}
