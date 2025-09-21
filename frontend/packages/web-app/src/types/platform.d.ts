export interface LoginWinState {
  width: number
  height: number
  center?: boolean
  resizable?: boolean
  maximized: boolean
}

export interface MainWinState extends LoginWinState {}
