import PageLayout from './components/Base/PageLayout.vue'
import LoginForm from './components/Login/Index.vue'
import LoginPage from './pages/LoginPage.vue'
import TenantDropdown from './components/Login/TenantDropdown.vue'
import Consult from './components/Base/Consult.vue'
import Invite from './components/Invite/Index.vue'
import InvitePage from './pages/InvitePage.vue'
import { logout } from './api/login'
import { getUserInfo } from './utils/remember'
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
  getUserInfo,
}

export * from './interface'
export default LoginForm
