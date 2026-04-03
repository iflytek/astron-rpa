/**
 * @file i18n type definitions
 */

export type Locale = 'en' | 'zh-CN' | 'ar'

export interface Messages {
  errors: {
    // Background errors
    tabGetError: string
    activeTabError: string
    numberIdError: string
    frameGetError: string
    currentTabUnsupportError: string
    notSimilarElement: string
    similarNotFound: string
    relativeElementParamsError: string
    elementNotFound: string
    unsupportError: string
    paramsUrlNotFound: string
    paramsNameNotFound: string
    paramsNameValueNotFound: string
    contextNotFound: string
    executeError: string
    debuggerTimeout: string
    contentMessageError: string

    // Content errors
    elementInfoIncomplete: string
    elementMultiFound: string
    elementNotInput: string
    elementNotChecked: string
    elementNotSelect: string
    elementNotTable: string
    elementParentNotFound: string
    elementChildNotFound: string
    elementChildOriginNotFound: string
    updateTip: string
    elementChangedAtNode: string
    syntaxError: string
    typeError: string
    referenceError: string
  }
  success: {
    deleteSuccess: string
    setSuccess: string
    emptySuccess: string
  }
  tags: {
    html: string
    body: string
    div: string
    span: string
    p: string
    a: string
    address: string
    area: string
    article: string
    audio: string
    b: string
    button: string
    canvas: string
    code: string
    col: string
    colgroup: string
    datalist: string
    details: string
    dialog: string
    em: string
    embed: string
    footer: string
    form: string
    frame: string
    h1: string
    h2: string
    h3: string
    h4: string
    h5: string
    h6: string
    header: string
    hr: string
    i: string
    iframe: string
    img: string
    input: string
    textarea: string
    label: string
    li: string
    main: string
    mark: string
    menu: string
    nav: string
    ol: string
    picture: string
    progress: string
    select: string
    summary: string
    table: string
    tr: string
    td: string
    ul: string
    video: string
    other: string
  }
  inputTypes: {
    text: string
    password: string
    checkbox: string
    radio: string
    submit: string
    reset: string
    button: string
    file: string
    hidden: string
    image: string
    email: string
    url: string
    tel: string
    number: string
    search: string
    range: string
    date: string
    time: string
    month: string
    week: string
    datetime: string
    color: string
  }
}
