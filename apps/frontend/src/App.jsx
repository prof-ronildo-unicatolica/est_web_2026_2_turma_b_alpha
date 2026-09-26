import { useEffect, useState } from 'react'

import Cadastro from './components/Cadastro'
import HomeBusca from './components/HomeBusca'
import Login from './components/Login'
import { apiFetch } from './services/api'

export default function App() {
  const [pagina, setPagina] = useState('home')
  const [usuario, setUsuario] = useState(null)

  useEffect(() => {
    async function carregarUsuario() {
      const token = localStorage.getItem('access_token')

      if (!token) {
        setUsuario(null)
        return
      }

      try {
        const resposta = await apiFetch('/auth/me')

        if (!resposta) {
          setUsuario(null)
          return
        }

        if (!resposta.ok) {
          localStorage.removeItem('access_token')
          setUsuario(null)
          return
        }

        const dadosUsuario = await resposta.json()
        setUsuario(dadosUsuario)
      } catch {
        setUsuario(null)
      }
    }

    carregarUsuario()
  }, [pagina])

  function logout() {
    localStorage.removeItem('access_token')
    setUsuario(null)
    setPagina('home')
  }

  return (
    <div className="min-vh-100 bg-light">
      {/* NAVEGAÇÃO */}
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

          <div
            className="collapse navbar-collapse"
            id="navbarPrincipal"
          >
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
            </ul>

            <div className="d-flex align-items-center gap-2">
              {usuario ? (
                <>
                  <span className="text-secondary small">
                    {usuario.nome || usuario.email || 'Usuário'}
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

      {/* TELA DE LOGIN */}
      {pagina === 'login' && (
        <div className="container">
          <Login
            onCadastro={() => setPagina('cadastro')}
            onVoltar={() => setPagina('home')}
            onLogin={() => setPagina('home')}
          />
        </div>
      )}

      {/* TELA DE CADASTRO */}
      {pagina === 'cadastro' && (
        <div className="container">
          <Cadastro
            onLogin={() => setPagina('login')}
            onVoltar={() => setPagina('home')}
          />
        </div>
      )}

      {/* HOME */}
      {pagina === 'home' && (
        <div className="container pb-5">
          <HomeBusca />
        </div>
      )}
    </div>
  )
}