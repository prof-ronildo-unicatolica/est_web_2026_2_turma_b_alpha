import { useState } from 'react'

export default function Login({ onCadastro, onVoltar, onLogin }) {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  async function handleLogin(e) {
    e.preventDefault()

    setErro('')
    setCarregando(true)

    try {
      const resposta = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email,
          senha: senha
        })
      })

      if (!resposta.ok) {
        if (resposta.status === 401) {
          setErro('E-mail ou senha inválidos.')
        } else {
          setErro('Não foi possível realizar o login.')
        }

        return
      }

      const dados = await resposta.json()

      // Armazena o access token
      localStorage.setItem('access_token', dados.access_token)
      console.log('Token salvo:', localStorage.getItem('access_token'))

      alert('Login realizado com sucesso!')
      
      onLogin()

      console.log('Login realizado:', dados)
    } catch (error) {
      console.error('Erro ao realizar login:', error)
      setErro('Não foi possível conectar ao servidor.')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow">
            <div className="card-body p-4">

              <h2 className="text-center text-primary mb-4">
                Login
              </h2>

              <form onSubmit={handleLogin}>

                <div className="mb-3">
                  <label className="form-label">
                    E-mail
                  </label>

                  <input
                    type="email"
                    className="form-control"
                    placeholder="Digite seu e-mail"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    Senha
                  </label>

                  <input
                    type="password"
                    className="form-control"
                    placeholder="Digite sua senha"
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
                    required
                  />
                </div>

                {erro && (
                  <div className="alert alert-danger">
                    {erro}
                  </div>
                )}

                <button
                  type="submit"
                  className="btn btn-primary w-100"
                  disabled={carregando}
                >
                  {carregando ? 'Entrando...' : 'Entrar'}
                </button>

              </form>

              <div className="text-center mt-4">
                <p className="mb-2">
                  Ainda não possui uma conta?
                </p>

                <button
                  className="btn btn-outline-primary"
                  onClick={onCadastro}
                >
                  Criar cadastro
                </button>
              </div>

              <div className="text-center mt-3">
                <button
                  className="btn btn-link"
                  onClick={onVoltar}
                >
                  Voltar
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  )
}