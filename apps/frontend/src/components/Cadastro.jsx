import { useState } from 'react'

export default function Cadastro({ onLogin, onVoltar }) {
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')

async function handleCadastro(e) {
  e.preventDefault()

  setErro('')
  setCarregando(true)

  try {
    const resposta = await fetch('http://localhost:8000/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        nome: nome,
        email: email,
        senha: senha
      })
    })

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => null)

      setErro(dados?.detail || 'Não foi possível realizar o cadastro.')
      return
    }

    alert('Cadastro realizado com sucesso!')
    onLogin()
  } catch (error) {
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
                Criar Cadastro
              </h2>

              {erro && (
                <div className="alert alert-danger">
                  {erro}
                </div>
              )}

              <form onSubmit={handleCadastro}>

                <div className="mb-3">
                  <label className="form-label">
                    Nome
                  </label>

                  <input
                    type="text"
                    className="form-control"
                    placeholder="Digite seu nome"
                    value={nome}
                    onChange={(e) => setNome(e.target.value)}
                    required
                  />
                </div>

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

                <button
                  type="submit"
                  className="btn btn-primary w-100"
                >
                  Cadastrar
                </button>

              </form>

              <div className="text-center mt-4">
                <p>
                  Já possui uma conta?
                </p>

                <button
                  className="btn btn-outline-primary"
                  onClick={onLogin}
                >
                  Fazer Login
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