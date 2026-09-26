import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Eye, EyeOff, LogIn, UserPlus, Lock, Mail, User, CheckCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { getErrorMessage } from '../utils/helpers.js'
import toast from 'react-hot-toast'

export default function Login() {
  const { login, register } = useAuth()
  const navigate = useNavigate()

  // Tab: 'login' | 'register'
  const [tab, setTab] = useState('login')

  // Login form
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [showLoginPwd, setShowLoginPwd] = useState(false)
  const [loginLoading, setLoginLoading] = useState(false)

  // Register form
  const [regForm, setRegForm] = useState({ name: '', email: '', password: '', confirm_password: '' })
  const [showRegPwd, setShowRegPwd] = useState(false)
  const [regLoading, setRegLoading] = useState(false)

  // ── LOGIN ──────────────────────────────────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginLoading(true)
    try {
      await login(loginForm.email, loginForm.password)
      toast.success('Welcome back! 👋')
      navigate('/dashboard')
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setLoginLoading(false)
    }
  }

  // ── REGISTER ───────────────────────────────────────────────────────────
  const handleRegister = async (e) => {
    e.preventDefault()
    if (regForm.password !== regForm.confirm_password) {
      toast.error('Passwords do not match.')
      return
    }
    if (regForm.password.length < 8) {
      toast.error('Password must be at least 8 characters.')
      return
    }
    setRegLoading(true)
    try {
      await register(regForm.name, regForm.email, regForm.password, regForm.confirm_password)
      toast.success('Account created! Welcome to PrivacyLens 🔒')
      navigate('/dashboard')
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setRegLoading(false)
    }
  }

  const updateReg = (field) => (e) => setRegForm(p => ({ ...p, [field]: e.target.value }))

  // Password strength indicator
  const pwdStrength = (pwd) => {
    if (!pwd) return null
    if (pwd.length < 6) return { label: 'Weak', color: 'bg-red-500', w: 'w-1/4' }
    if (pwd.length < 8) return { label: 'Fair', color: 'bg-orange-500', w: 'w-2/4' }
    if (pwd.length >= 8 && /[A-Z]/.test(pwd) && /[0-9]/.test(pwd)) return { label: 'Strong', color: 'bg-green-500', w: 'w-full' }
    return { label: 'Good', color: 'bg-yellow-500', w: 'w-3/4' }
  }
  const strength = pwdStrength(regForm.password)

  return (
    <div className="min-h-screen bg-gray-950 flex">
      {/* ── Left panel — branding ─────────────────────────────────────── */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-gray-900 via-dark-900 to-primary-900/30 flex-col justify-between p-12 relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary-600/10 rounded-full blur-3xl" />
          <div className="absolute bottom-1/3 right-1/4 w-56 h-56 bg-indigo-600/10 rounded-full blur-3xl" />
        </div>

        {/* Logo */}
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-11 h-11 rounded-xl bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-600/30">
              <Shield size={22} className="text-white" />
            </div>
            <div>
              <p className="text-white font-bold text-lg leading-none">PrivacyLens</p>
              <p className="text-gray-500 text-xs">Data Protection Suite</p>
            </div>
          </div>
        </div>

        {/* Center content */}
        <div className="relative z-10 space-y-8">
          <div>
            <h2 className="text-4xl font-bold text-white leading-tight">
              Protect Your<br />
              <span className="text-primary-400">Sensitive Data</span><br />
              Before It's Too Late
            </h2>
            <p className="text-gray-400 mt-4 text-base leading-relaxed">
              AI-powered detection of passwords, API keys, government IDs,
              financial data and more — before you share a document.
            </p>
          </div>

          {/* Feature bullets */}
          <div className="space-y-3">
            {[
              '15+ sensitive data detectors',
              'PDF, DOCX, Image & text scanning',
              'Risk scoring & PDF reports',
              'Automatic data masking',
            ].map((f) => (
              <div key={f} className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full bg-primary-600/20 border border-primary-600/40 flex items-center justify-center flex-shrink-0">
                  <CheckCircle size={12} className="text-primary-400" />
                </div>
                <span className="text-gray-300 text-sm">{f}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="relative z-10">
          <p className="text-gray-600 text-xs">B.Tech Cybersecurity Project · PrivacyLens v1.0</p>
        </div>
      </div>

      {/* ── Right panel — forms ───────────────────────────────────────── */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-10">
        <div className="w-full max-w-md">

          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary-600 mb-3">
              <Shield size={22} className="text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">PrivacyLens</h1>
          </div>

          {/* Tab switcher */}
          <div className="flex bg-gray-900 rounded-xl p-1 mb-7 border border-gray-800">
            <button
              onClick={() => setTab('login')}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                tab === 'login'
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/25'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <LogIn size={15} /> Sign In
            </button>
            <button
              onClick={() => setTab('register')}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                tab === 'register'
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/25'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <UserPlus size={15} /> Create Account
            </button>
          </div>

          {/* ── LOGIN FORM ──────────────────────────────────────────────── */}
          {tab === 'login' && (
            <div className="card border-gray-800">
              <h2 className="text-xl font-bold text-white mb-1">Welcome back</h2>
              <p className="text-gray-500 text-sm mb-6">Sign in to your PrivacyLens account</p>

              <form onSubmit={handleLogin} className="space-y-4">
                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                    <input
                      type="email" required
                      className="input-field pl-10"
                      placeholder="you@example.com"
                      value={loginForm.email}
                      onChange={e => setLoginForm(p => ({ ...p, email: e.target.value }))}
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                    <input
                      type={showLoginPwd ? 'text' : 'password'} required
                      className="input-field pl-10 pr-11"
                      placeholder="••••••••"
                      value={loginForm.password}
                      onChange={e => setLoginForm(p => ({ ...p, password: e.target.value }))}
                    />
                    <button type="button"
                      onClick={() => setShowLoginPwd(p => !p)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors">
                      {showLoginPwd ? <EyeOff size={17} /> : <Eye size={17} />}
                    </button>
                  </div>
                </div>

                <button type="submit" disabled={loginLoading} className="btn-primary w-full justify-center py-3 mt-1">
                  {loginLoading
                    ? <><span className="animate-spin rounded-full h-4 w-4 border-t-2 border-white" /> Signing in…</>
                    : <><LogIn size={17} /> Sign In</>
                  }
                </button>
              </form>

              <div className="mt-5 pt-5 border-t border-gray-800 text-center">
                <p className="text-gray-500 text-sm">
                  Don't have an account?{' '}
                  <button onClick={() => setTab('register')} className="text-primary-400 hover:text-primary-300 font-semibold transition-colors">
                    Create one free →
                  </button>
                </p>
              </div>
            </div>
          )}

          {/* ── REGISTER FORM ───────────────────────────────────────────── */}
          {tab === 'register' && (
            <div className="card border-gray-800">
              <h2 className="text-xl font-bold text-white mb-1">Create your account</h2>
              <p className="text-gray-500 text-sm mb-6">Free forever · No credit card required</p>

              <form onSubmit={handleRegister} className="space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Full Name</label>
                  <div className="relative">
                    <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                    <input
                      type="text" required
                      className="input-field pl-10"
                      placeholder="Arjun Kumar"
                      value={regForm.name}
                      onChange={updateReg('name')}
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Email Address</label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                    <input
                      type="email" required
                      className="input-field pl-10"
                      placeholder="you@example.com"
                      value={regForm.email}
                      onChange={updateReg('email')}
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                    <input
                      type={showRegPwd ? 'text' : 'password'} required
                      className="input-field pl-10 pr-11"
                      placeholder="Min. 8 characters"
                      value={regForm.password}
                      onChange={updateReg('password')}
                    />
                    <button type="button"
                      onClick={() => setShowRegPwd(p => !p)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors">
                      {showRegPwd ? <EyeOff size={17} /> : <Eye size={17} />}
                    </button>
                  </div>
                  {/* Password strength bar */}
                  {strength && (
                    <div className="mt-2">
                      <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all duration-300 ${strength.color} ${strength.w}`} />
                      </div>
                      <p className={`text-xs mt-1 ${
                        strength.label === 'Weak' ? 'text-red-400' :
                        strength.label === 'Fair' ? 'text-orange-400' :
                        strength.label === 'Good' ? 'text-yellow-400' : 'text-green-400'
                      }`}>{strength.label} password</p>
                    </div>
                  )}
                </div>

                {/* Confirm Password */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Confirm Password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                    <input
                      type="password" required
                      className={`input-field pl-10 ${
                        regForm.confirm_password && regForm.confirm_password !== regForm.password
                          ? 'border-red-600 focus:ring-red-500'
                          : regForm.confirm_password && regForm.confirm_password === regForm.password
                          ? 'border-green-600 focus:ring-green-500'
                          : ''
                      }`}
                      placeholder="Repeat password"
                      value={regForm.confirm_password}
                      onChange={updateReg('confirm_password')}
                    />
                    {regForm.confirm_password && regForm.confirm_password === regForm.password && (
                      <CheckCircle size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500" />
                    )}
                  </div>
                  {regForm.confirm_password && regForm.confirm_password !== regForm.password && (
                    <p className="text-xs text-red-400 mt-1">Passwords do not match</p>
                  )}
                </div>

                <button type="submit" disabled={regLoading} className="btn-primary w-full justify-center py-3 mt-1">
                  {regLoading
                    ? <><span className="animate-spin rounded-full h-4 w-4 border-t-2 border-white" /> Creating account…</>
                    : <><UserPlus size={17} /> Create Account</>
                  }
                </button>
              </form>

              <div className="mt-5 pt-5 border-t border-gray-800 text-center">
                <p className="text-gray-500 text-sm">
                  Already have an account?{' '}
                  <button onClick={() => setTab('login')} className="text-primary-400 hover:text-primary-300 font-semibold transition-colors">
                    Sign in →
                  </button>
                </p>
              </div>
            </div>
          )}

          {/* Security note */}
          <div className="mt-4 flex items-center justify-center gap-2 text-gray-600">
            <Lock size={11} />
            <p className="text-xs">Passwords are bcrypt hashed · JWT secured · No plain-text storage</p>
          </div>
        </div>
      </div>
    </div>
  )
}
