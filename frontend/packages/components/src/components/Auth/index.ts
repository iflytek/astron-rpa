import PageLayout from './components/Base/PageLayout.vue'
import LoginForm from './components/Login/Index.vue'
import LoginPage from './pages/LoginPage.vue'
import TenantDropdown from './components/Login/TenantDropdown.vue'
import TenantUpgradeBtn from './components/Base/TenantUpgradeBtn.vue'
import MarketInviteForm from './components/MarketInvite/Index.vue'
import MarketInvitePage from './pages/MarketInvitePage.vue'
import EnterpriseInviteForm from './components/EnterpriseInvite/Index.vue'
import EnterpriseInvitePage from './pages/EnterpriseInvitePage.vue'
import { logout } from './api/login'
import { getUserInfo } from './utils/remember'
import './style/index.scss'
export const Auth = {
  PageLayout,
  LoginForm,
  LoginPage,
  TenantDropdown,
  TenantUpgradeBtn,
  MarketInvitePage,
  MarketInviteForm,
  EnterpriseInvitePage,
  EnterpriseInviteForm,
  logout,
  getUserInfo,
}

export * from './interface'
export default LoginForm
