// Register page redirects to Login page which contains both Login + Register tabs
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Register() {
  const navigate = useNavigate()
  useEffect(() => {
    navigate('/login', { replace: true })
  }, [])
  return null
}
