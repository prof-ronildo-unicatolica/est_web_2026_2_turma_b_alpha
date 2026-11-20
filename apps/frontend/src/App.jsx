import { useEffect, useState } from 'react'

import Cadastro from './components/Cadastro'
import HomeBusca from './components/HomeBusca'
import Login from './components/Login'
import { apiFetch } from './services/api'
import Checkout from './components/Checkout'
import { ReservasPage } from './components/ReservasPage'

export default function App() {
  const [pagina, setPagina] = useState('home')
  const [token, setToken] = useState(() => localStorage.getItem('access_token') || '')
  const [usuario, setUsuario] = useState(null)
  const [reservaSelecionada, setReservaSelecionada] = useState(null)

  useEffect(() => {
    async function carregarUsuario() {
      const tokenAtual = localStorage.getItem('access_token') || ''
      setToken(tokenAtual)

      if (!tokenAtual) {
        setUsuario(null)
        return
      }

      try {
        let resposta = await apiFetch('/api/v1/auth/me')
        if (resposta && resposta.status === 404) {
          resposta = await apiFetch('/auth/me')
        }

        if (!resposta) {
          setToken('')
          setUsuario(null)
          return
        }

        if (!resposta.ok) {
          setUsuario({ email: 'Usuário autenticado' })
          return
        }

        const dadosUsuario = await resposta.json()
        setUsuario(dadosUsuario)
      } catch {
        setUsuario({ email: 'Usuário autenticado' })
      }
    }

    carregarUsuario()
  }, [pagina])

  function handleSucessoLogin(dadosLogin) {
    const novoToken = localStorage.getItem('access_token') || ''
    setToken(novoToken)
    setUsuario(dadosLogin?.usuario || { email: 'Usuário autenticado' })
    setPagina('reservas')
  }

  function logout() {
    localStorage.removeItem('access_token')
    setToken('')
    setUsuario(null)
    setPagina('home')
  }

  const estaLogado = Boolean(token)

  return (
    <div className="min-vh-100 bg-light">
      <nav className="navbar navbar-expand-lg bg-white shadow-sm mb-4">
        <div className="container">
          <button
            className="navbar-brand btn btn-link text-decoration-none fw-bold text-primary p-0"
            type="button"
            onClick={() => setPagina('home')}
          >
            Hotel Alpha
          </button>

          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarPrincipal"
            aria-controls="navbarPrincipal"
            aria-expanded="false"
            aria-label="Abrir navegação"
          >
            <span className="navbar-toggler-icon" />
          </button>

          <div className="collapse navbar-collapse" id="navbarPrincipal">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <button
                  className="nav-link btn btn-link"
                  type="button"
                  onClick={() => setPagina('home')}
                >
                  Hotéis
                </button>
              </li>

              <li className="nav-item">
                <button
                  className={`nav-link btn btn-link ${pagina === 'reservas' ? 'active fw-semibold' : ''}`}
                  type="button"
                  onClick={() => setPagina('reservas')}
                >
                  Minhas Reservas
                </button>
              </li>
            </ul>

            <div className="d-flex align-items-center gap-2">
              {estaLogado ? (
                <>
                  <span className="text-secondary small">
                    {usuario?.nome || usuario?.email || 'Usuário autenticado'}
                  </span>

                  <button
                    className="btn btn-outline-danger btn-sm"
                    type="button"
                    onClick={logout}
                  >
                    Sair
                  </button>
                </>
              ) : (
                <>
                  <button
                    className="btn btn-outline-primary btn-sm px-3"
                    type="button"
                    onClick={() => setPagina('login')}
                  >
                    Login
                  </button>

                  <button
                    className="btn btn-primary btn-sm px-3"
                    type="button"
                    onClick={() => setPagina('cadastro')}
                  >
                    Criar conta
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {pagina === 'login' && (
        <div className="container">
          <Login
            onCadastro={() => setPagina('cadastro')}
            onVoltar={() => setPagina('home')}
            onLogin={handleSucessoLogin}
          />
        </div>
      )}

      {pagina === 'cadastro' && (
        <div className="container">
          <Cadastro
            onLogin={() => setPagina('login')}
            onVoltar={() => setPagina('home')}
          />
        </div>
      )}

      {pagina === 'home' && (
        <div className="container pb-5">
          <HomeBusca
            onCheckout={(dados) => {
              setReservaSelecionada(dados)
              setPagina('checkout')
            }}
          />
        </div>
      )}

      {pagina === 'checkout' && (
        <Checkout
          reserva={reservaSelecionada}
          onVoltar={() => setPagina('home')}
        />
      )}

      {pagina === 'reservas' && (
        <div className="container pb-5">
          <ReservasPage
            tokenProp={token}
            reservaInicial={reservaSelecionada}
            onVoltar={() => setPagina('home')}
          />
        </div>
      )}
    </div>
  )
}