import { useEffect, useMemo, useState } from 'react'

const API = 'http://localhost:8000/api/v1'

function HotelSkeleton() {
  return (
    <div className="col-md-6 col-lg-4">
      <div className="card shadow-sm h-100">
        <div className="card-body">
          <div className="placeholder-glow">
            <span className="placeholder col-8 mb-3"></span>
            <span className="placeholder col-6 mb-2"></span>
            <span className="placeholder col-4"></span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function HomeBusca() {
  const [cidades, setCidades] = useState([])
  const [hoteis, setHoteis] = useState([])
  const [quartosPorHotel, setQuartosPorHotel] = useState({})

  const [cidadeId, setCidadeId] = useState('')
  const [checkIn, setCheckIn] = useState('')
  const [checkOut, setCheckOut] = useState('')
  const [adultos, setAdultos] = useState(1)
  const [criancas, setCriancas] = useState(0)
  const [estrelas, setEstrelas] = useState('')

  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [hotelSelecionado, setHotelSelecionado] = useState(null)

  useEffect(() => {
    async function carregarDados() {
      setCarregando(true)
      setErro('')

      try {
        const [resCidades, resHoteis] = await Promise.all([
          fetch(`${API}/cidades`),
          fetch(`${API}/hoteis`),
        ])

        if (!resCidades.ok) {
          throw new Error('Não foi possível carregar as cidades.')
        }

        if (!resHoteis.ok) {
          throw new Error('Não foi possível carregar os hotéis.')
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

  const hoteisFiltrados = useMemo(() => {
    return hoteis.filter((hotel) => {
      const atendeCidade =
        !cidadeId || hotel.cidade?.id === cidadeId

      const atendeEstrelas =
        !estrelas || hotel.estrelas === Number(estrelas)

      return atendeCidade && atendeEstrelas
    })
  }, [hoteis, cidadeId, estrelas])

  async function abrirDetalhes(hotel) {
    setHotelSelecionado(hotel)
    setErro('')

    if (quartosPorHotel[hotel.id]) {
      return
    }

    try {
      const resposta = await fetch(
        `${API}/quartos?hotel_id=${encodeURIComponent(hotel.id)}`
      )

      if (!resposta.ok) {
        throw new Error('Não foi possível carregar os quartos do hotel.')
      }

      const quartos = await resposta.json()

      setQuartosPorHotel((estadoAtual) => ({
        ...estadoAtual,
        [hotel.id]: quartos,
      }))
    } catch (error) {
      setErro(error.message)
    }
  }

  function quartoAtendeCapacidade(quarto) {
    return (
      quarto.max_adultos >= Number(adultos) &&
      quarto.max_criancas >= Number(criancas)
    )
  }

  const quartosSelecionados = hotelSelecionado
    ? quartosPorHotel[hotelSelecionado.id] || []
    : []

  const quartosCompativeis = quartosSelecionados.filter(
    quartoAtendeCapacidade
  )

  return (
    <div>
      <section className="bg-white rounded shadow-sm p-4 mb-4">
        <div className="mb-4">
          <h1 className="fw-bold text-primary mb-2">
            Encontre seu hotel
          </h1>
          <p className="text-secondary mb-0">
            Busque hotéis e consulte quartos de acordo com a capacidade
            necessária.
          </p>
        </div>

        <div className="row g-3">
          <div className="col-md-4">
            <label className="form-label">Cidade</label>
            <select
              className="form-select"
              value={cidadeId}
              onChange={(event) => setCidadeId(event.target.value)}
            >
              <option value="">Todas as cidades</option>

              {cidades.map((cidade) => (
                <option key={cidade.id} value={cidade.id}>
                  {cidade.nome}
                </option>
              ))}
            </select>
          </div>

          <div className="col-md-2">
            <label className="form-label">Check-in</label>
            <input
              type="date"
              className="form-control"
              value={checkIn}
              onChange={(event) => setCheckIn(event.target.value)}
            />
          </div>

          <div className="col-md-2">
            <label className="form-label">Check-out</label>
            <input
              type="date"
              className="form-control"
              min={checkIn || undefined}
              value={checkOut}
              onChange={(event) => setCheckOut(event.target.value)}
            />
          </div>

          <div className="col-md-2">
            <label className="form-label">Adultos</label>
            <input
              type="number"
              className="form-control"
              min="1"
              value={adultos}
              onChange={(event) => setAdultos(event.target.value)}
            />
          </div>

          <div className="col-md-2">
            <label className="form-label">Crianças</label>
            <input
              type="number"
              className="form-control"
              min="0"
              value={criancas}
              onChange={(event) => setCriancas(event.target.value)}
            />
          </div>

          <div className="col-md-3">
            <label className="form-label">Estrelas</label>
            <select
              className="form-select"
              value={estrelas}
              onChange={(event) => setEstrelas(event.target.value)}
            >
              <option value="">Todas</option>
              {[1, 2, 3, 4, 5].map((quantidade) => (
                <option key={quantidade} value={quantidade}>
                  {quantidade} {quantidade === 1 ? 'estrela' : 'estrelas'}
                </option>
              ))}
            </select>
          </div>
        </div>

        {(checkIn || checkOut) && (
          <div className="alert alert-info mt-3 mb-0 py-2">
            As datas serão utilizadas no fluxo de disponibilidade da
            reserva. A API atual ainda não disponibiliza consulta de
            disponibilidade por período.
          </div>
        )}
      </section>

      {erro && (
        <div className="alert alert-danger" role="alert">
          {erro}
        </div>
      )}

      {carregando ? (
        <div className="row g-4">
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <HotelSkeleton key={item} />
          ))}
        </div>
      ) : (
        <>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h2 className="h4 mb-0">Hotéis encontrados</h2>
            <span className="text-secondary">
              {hoteisFiltrados.length} resultado(s)
            </span>
          </div>

          {hoteisFiltrados.length === 0 ? (
            <div className="alert alert-secondary">
              Nenhum hotel encontrado para os filtros selecionados.
            </div>
          ) : (
            <div className="row g-4">
              {hoteisFiltrados.map((hotel) => (
                <div
                  className="col-md-6 col-lg-4"
                  key={hotel.id}
                >
                  <div className="card shadow-sm h-100">
                    <div className="card-body d-flex flex-column">
                      <h3 className="h5 card-title fw-bold">
                        {hotel.nome}
                      </h3>

                      <p className="text-secondary mb-2">
                        {hotel.cidade?.nome}
                      </p>

                      <div
                        className="mb-4"
                        aria-label={`${hotel.estrelas} estrelas`}
                      >
                        {'★'.repeat(hotel.estrelas)}
                        <span className="text-muted">
                          {'☆'.repeat(5 - hotel.estrelas)}
                        </span>
                      </div>

                      <button
                        type="button"
                        className="btn btn-primary mt-auto"
                        onClick={() => abrirDetalhes(hotel)}
                      >
                        Ver quartos
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {hotelSelecionado && (
        <section className="bg-white rounded shadow-sm p-4 mt-5">
          <div className="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h2 className="h3 fw-bold mb-1">
                {hotelSelecionado.nome}
              </h2>
              <p className="text-secondary mb-0">
                {hotelSelecionado.cidade?.nome}
              </p>
            </div>

            <button
              type="button"
              className="btn-close"
              aria-label="Fechar"
              onClick={() => setHotelSelecionado(null)}
            />
          </div>

          {quartosSelecionados.length === 0 ? (
            <div className="alert alert-secondary">
              Nenhum quarto cadastrado para este hotel.
            </div>
          ) : quartosCompativeis.length === 0 ? (
            <div className="alert alert-warning">
              Existem quartos cadastrados, mas nenhum atende à capacidade
              de {adultos} adulto(s) e {criancas} criança(s).
            </div>
          ) : (
            <div className="row g-3">
              {quartosCompativeis.map((quarto) => (
                <div className="col-md-6" key={quarto.id}>
                  <div className="border rounded p-3 h-100">
                    <h3 className="h5 fw-bold">{quarto.tipo}</h3>

                    <p className="fs-5 text-primary fw-bold mb-2">
                      R$ {Number(quarto.preco_diaria).toFixed(2)}
                      <span className="fs-6 text-secondary fw-normal">
                        {' '}
                        / diária
                      </span>
                    </p>

                    <p className="mb-1">
                      Adultos: até {quarto.max_adultos}
                    </p>

                    <p className="mb-0">
                      Crianças: até {quarto.max_criancas}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  )
}