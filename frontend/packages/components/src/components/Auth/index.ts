import { logout, userInfo } from './api/login'
import Consult from './components/Base/Consult/Index.vue'
import PageLayout from './components/Base/PageLayout/Index.vue'
import Invite from './components/Invite/Index.vue'
import LoginForm from './components/Login/Index.vue'
import TenantDropdown from './components/Login/TenantDropdown.vue'
import InvitePage from './pages/InvitePage.vue'
import LoginPage from './pages/LoginPage.vue'
import './style/index.scss'

export const Auth = {
  PageLayout,
  LoginForm,
  LoginPage,
  TenantDropdown,
  Consult,
  InvitePage,
  Invite,
  logout,
  userInfo,
}

export * from './interface'
export default LoginForm
