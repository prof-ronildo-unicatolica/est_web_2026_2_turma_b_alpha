import { useEffect, useState } from 'react'

const API = 'http://localhost:8000/api/v1'

export default function AdminCatalogo({ onVoltar }) {
  const [aba, setAba] = useState('cidades')

   const [cidades, setCidades] = useState([])
   const [hoteis, setHoteis] = useState([])

   const [carregando, setCarregando] = useState(true)
   const [erro, setErro] = useState('')
   useEffect(() => {
    async function carregarDados() {
      try {
        const [resCidades, resHoteis] = await Promise.all([
          fetch(`${API}/cidades`),
          fetch(`${API}/hoteis`),
        ])

        if (!resCidades.ok || !resHoteis.ok) {
          throw new Error('Erro ao carregar dados do catálogo.')
        }

        const dadosCidades = await resCidades.json()
        const dadosHoteis = await resHoteis.json()

        setCidades(dadosCidades)
        setHoteis(dadosHoteis)
      } catch (error) {
        setErro(error.message)
      } finally {
        setCarregando(false)
      }
    }

  carregarDados()
}, [])

   const [nomeCidade, setNomeCidade] = useState('')
   const [nomeHotel, setNomeHotel] = useState('')
   const [cidadeHotel, setCidadeHotel] = useState('')

async function cadastrarCidade(event) {
  event.preventDefault()

  if (!nomeCidade.trim()) {
    setErro('Preencha o nome da cidade.')
    return
  }

  try {
    const resposta = await fetch(`${API}/cidades`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        nome: nomeCidade.trim(),
      }),
    })

    const dados = await resposta.json()

    if (!resposta.ok) {
      throw new Error(dados.detail || 'Erro ao cadastrar cidade.')
    }

    setCidades([...cidades, dados])
    setNomeCidade('')
    setErro('')
  } catch (error) {
    setErro(error.message)
  }
}


async function cadastrarHotel(event) {
  event.preventDefault()

  if (!nomeHotel.trim() || !cidadeHotel) {
    setErro('Preencha o nome do hotel e selecione a cidade.')
    return
  }

  try {
    const resposta = await fetch(`${API}/hoteis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        nome: nomeHotel.trim(),
        cidade_id: cidadeHotel,
      }),
    })

    const dados = await resposta.json()

    if (!resposta.ok) {
      throw new Error(dados.detail || 'Erro ao cadastrar hotel.')
    }

    setHoteis([...hoteis, dados])
    setNomeHotel('')
    setCidadeHotel('')
    setErro('')
  } catch (error) {
    setErro(error.message)
  }
}



  return (
    <div className="container py-4">
      <button
      type="button"
      className="btn btn-outline-secondary mb-3"
      onClick={onVoltar}
    >
      ← Voltar 
    </button>
      <h1 className="fw-bold">Painel Administrativo</h1>

      <p className="text-secondary">
        Gerenciamento de Cidades e Hotéis
      </p>

      {carregando && (
        <div className="alert alert-info">
          Carregando dados do catálogo...
        </div>
      )}

      <div className="d-flex gap-2 mb-4">
        <button
          type="button"
          className={`btn ${
            aba === 'cidades' ? 'btn-primary' : 'btn-outline-primary'
          }`}
          onClick={() => setAba('cidades')}
        >
          Cidades
        </button>

        <button
          type="button"
          className={`btn ${
            aba === 'hoteis' ? 'btn-primary' : 'btn-outline-primary'
          }`}
          onClick={() => setAba('hoteis')}
        >
          Hotéis
        </button>
      </div>

      {aba === 'cidades' && (
        <div className="row g-4">
          <div className="col-md-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5">
                  Cadastrar Cidade
                </h2>

                <form onSubmit={cadastrarCidade}>
                  <div className="mb-3">
                    <label className="form-label">Nome da cidade</label>

                    <input
                      type="text"
                      className="form-control"
                      placeholder="Digite o nome da cidade"
                      value={nomeCidade}
                      onChange={(event) => setNomeCidade(event.target.value)}
                    />
                  </div>

                  {erro && (
                    <div className="alert alert-danger">
                      {erro}
                    </div>
                  )}

                  <button type="submit" className="btn btn-primary">
                    Cadastrar
                  </button>
                </form>
              </div>
            </div>
          </div>

          <div className="col-md-8">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5">Cidades cadastradas</h2>

                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Cidade</th>
                      </tr>
                    </thead>

                    <tbody>
                      {cidades.map((cidade) => (
                        <tr key={cidade.id}>
                          <td>{cidade.id}</td>
                          <td>{cidade.nome}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {aba === 'hoteis' && (
  <div className="row g-4">
    <div className="col-md-4">
      <div className="card shadow-sm">
        <div className="card-body">
          <h2 className="h5">
            Cadastrar Hotel
          </h2>

            <form
              onSubmit={cadastrarHotel}
            > 
            <div className="mb-3">
              <label className="form-label">
                Nome do hotel
              </label>

              <input
                type="text"
                className="form-control"
                placeholder="Digite o nome do hotel"
                value={nomeHotel}
                onChange={(event) =>
                  setNomeHotel(event.target.value)
                }
              />
            </div>

            <div className="mb-3">
              <label className="form-label">
                Cidade
              </label>

              <select
                className="form-select"
                value={cidadeHotel}
                onChange={(event) => setCidadeHotel(event.target.value)}
              >
                <option value="">Selecione uma cidade</option>

                {cidades.map((cidade) => (
                  <option key={cidade.id} value={cidade.id}>
                    {cidade.nome}
                  </option>
                ))}
              </select>
            </div>

            

            {erro && (
              <div className="alert alert-danger">
                {erro}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary"
            >
              Cadastrar
            </button>
          </form>
        </div>
      </div>
    </div>

    <div className="col-md-8">
      <div className="card shadow-sm">
        <div className="card-body">
          <h2 className="h5">Hotéis cadastrados</h2>

          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Hotel</th>
                  <th>Cidade</th>
                </tr>
              </thead>

              <tbody>
                {hoteis.map((hotel) => (
                  <tr key={hotel.id}>
                    <td>{hotel.id}</td>
                    <td>{hotel.nome}</td>
                    <td>{hotel.cidade?.nome}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
)}
    </div>
  )
}