import LoginForm from './components/Login/Index.vue'
import MarketInviteForm from './components/MarketInvite/Index.vue'
import BackButton from './components/Base/BackButton.vue'
import LoginPage from './pages/LoginPage.vue'
import MarketInvitePage from './pages/MarketInvitePage.vue'
import EnterpriseInviteForm from './components/EnterpriseInvite/Index.vue'
import EnterpriseInvitePage from './pages/EnterpriseInvitePage.vue'
import './style/index.scss'
export const Auth = {
  LoginForm,
  LoginPage,
  EnterpriseInviteForm,
  EnterpriseInvitePage,
  MarketInviteForm,
  MarketInvitePage,
  BackButton,
}

export type * from './interface'

export { useAuth } from './hooks/useAuth'

export default LoginForm
