import { useState } from 'react'

export default function AdminCatalogo() {
  const [aba, setAba] = useState('cidades')

  const [cidades, setCidades] = useState([
    { id: 1, nome: 'Fortaleza', estado: 'CE' },
    { id: 2, nome: 'Quixadá', estado: 'CE' },
  ])

  const [nomeCidade, setNomeCidade] = useState('')
  const [estadoCidade, setEstadoCidade] = useState('')
  const [erro, setErro] = useState('')
  const [cidadeEditando, setCidadeEditando] = useState(null)

  const [hoteis, setHoteis] = useState([
  {
    id: 1,
    nome: 'Hotel Alpha',
    cidade: 'Fortaleza',
    estrelas: 4,
  },
  {
    id: 2,
    nome: 'Hotel Central',
    cidade: 'Quixadá',
    estrelas: 3,
  },
])

const [nomeHotel, setNomeHotel] = useState('')
const [cidadeHotel, setCidadeHotel] = useState('')
const [estrelasHotel, setEstrelasHotel] = useState('1')
const [hotelEditando, setHotelEditando] = useState(null)

  function cadastrarCidade(event) {
    event.preventDefault()

    if (!nomeCidade.trim() || !estadoCidade.trim()) {
      setErro('Preencha o nome da cidade e o estado.')
      return
    }

    const novaCidade = {
      id: cidades.length + 1,
      nome: nomeCidade,
      estado: estadoCidade.toUpperCase(),
    }

    setCidades([...cidades, novaCidade])

    setNomeCidade('')
    setEstadoCidade('')
    setErro('')
  }
  function editarCidade(cidade) {
  setCidadeEditando(cidade.id)
  setNomeCidade(cidade.nome)
  setEstadoCidade(cidade.estado)
  setErro('')
}

function salvarEdicaoCidade(event) {
  event.preventDefault()

  if (!nomeCidade.trim() || !estadoCidade.trim()) {
    setErro('Preencha o nome da cidade e o estado.')
    return
  }

  setCidades(
    cidades.map((cidade) =>
      cidade.id === cidadeEditando
        ? {
            ...cidade,
            nome: nomeCidade,
            estado: estadoCidade.toUpperCase(),
          }
        : cidade
    )
  )

  setCidadeEditando(null)
  setNomeCidade('')
  setEstadoCidade('')
  setErro('')
}

  function cadastrarHotel(event) {
  event.preventDefault()

  if (!nomeHotel.trim() || !cidadeHotel.trim()) {
    setErro('Preencha o nome do hotel e a cidade.')
    return
  }

  const novoHotel = {
    id: hoteis.length + 1,
    nome: nomeHotel,
    cidade: cidadeHotel,
    estrelas: Number(estrelasHotel),
  }

  setHoteis([...hoteis, novoHotel])

  setNomeHotel('')
  setCidadeHotel('')
  setEstrelasHotel('1')
  setErro('')
}

function editarHotel(hotel) {
  setHotelEditando(hotel.id)
  setNomeHotel(hotel.nome)
  setCidadeHotel(hotel.cidade)
  setEstrelasHotel(String(hotel.estrelas))
  setErro('')
}

function salvarEdicaoHotel(event) {
  event.preventDefault()

  if (!nomeHotel.trim() || !cidadeHotel.trim()) {
    setErro('Preencha o nome do hotel e a cidade.')
    return
  }

  setHoteis(
    hoteis.map((hotel) =>
      hotel.id === hotelEditando
        ? {
            ...hotel,
            nome: nomeHotel,
            cidade: cidadeHotel,
            estrelas: Number(estrelasHotel),
          }
        : hotel
    )
  )

  setHotelEditando(null)
  setNomeHotel('')
  setCidadeHotel('')
  setEstrelasHotel('1')
  setErro('')
}

  return (
    <div className="container py-4">
      <h1 className="fw-bold">Painel Administrativo</h1>

      <p className="text-secondary">
        Gerenciamento de Cidades e Hotéis
      </p>

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
          className="btn btn-outline-primary"
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
                  {cidadeEditando ? 'Editar Cidade' : 'Cadastrar Cidade'}
                </h2>

                <form
                  onSubmit={
                    cidadeEditando
                      ?salvarEdicaoCidade
                      : cadastrarCidade
                    }
                >
                  <div className="mb-3">
                    <label className="form-label">Nome</label>

                    <input
                      type="text"
                      className="form-control"
                      value={nomeCidade}
                      onChange={(event) =>
                        setNomeCidade(event.target.value)
                      }
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Estado</label>

                    <input
                      type="text"
                      className="form-control"
                      maxLength="2"
                      value={estadoCidade}
                      onChange={(event) =>
                        setEstadoCidade(event.target.value)
                      }
                    />
                  </div>

                  {erro && (
                    <div className="alert alert-danger">
                      {erro}
                    </div>
                  )}

                  <button type="submit" className="btn btn-primary">
                    {cidadeEditando ? 'Salvar alterações' : 'Cadastrar'}
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
                        <th>Estado</th>
                        <th>Ações</th>
                      </tr>
                    </thead>

                    <tbody>
                      {cidades.map((cidade) => (
                        <tr key={cidade.id}>
                          <td>{cidade.id}</td>
                          <td>{cidade.nome}</td>
                          <td>{cidade.estado}</td>
                          <td>
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => editarCidade(cidade)}
                            >
                              Editar
                            </button>
                          </td>
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
            {hotelEditando ? 'Editar Hotel' : 'Cadastrar Hotel'}
          </h2>

            <form
              onSubmit={
              hotelEditando
                ? salvarEdicaoHotel
                : cadastrarHotel
              }
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

              <input
                type="text"
                className="form-control"
                placeholder="Digite a cidade"
                value={cidadeHotel}
                onChange={(event) =>
                  setCidadeHotel(event.target.value)
                }
              />
            </div>

            <div className="mb-3">
              <label className="form-label">
                Estrelas
              </label>

              <select
                className="form-select"
                value={estrelasHotel}
                onChange={(event) =>
                  setEstrelasHotel(event.target.value)
                }
              >
                <option value="1">1 estrela</option>
                <option value="2">2 estrelas</option>
                <option value="3">3 estrelas</option>
                <option value="4">4 estrelas</option>
                <option value="5">5 estrelas</option>
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
              {hotelEditando ? 'Salvar alterações' : 'Cadastrar'}
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
                  <th>Estrelas</th>
                  <th>Ações</th>
                </tr>
              </thead>

              <tbody>
                {hoteis.map((hotel) => (
                  <tr key={hotel.id}>
                    <td>{hotel.id}</td>
                    <td>{hotel.nome}</td>
                    <td>{hotel.cidade}</td>
                    <td>{hotel.estrelas} ⭐</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => editarHotel(hotel)}
                      >
                        Editar
                      </button>
                    </td>
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