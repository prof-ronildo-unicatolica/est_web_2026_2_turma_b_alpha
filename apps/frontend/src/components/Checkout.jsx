import { useEffect, useState } from 'react'
import { apiFetch } from '../services/api'

const API = 'http://localhost:8000/api/v1'

export default function Checkout({ reserva, onVoltar }) {
  const [tarifaSelecionada, setTarifaSelecionada] = useState('')
  const [servicosSelecionados, setServicosSelecionados] = useState([])

  const [tarifas, setTarifas] = useState([])
  const [servicos, setServicos] = useState([])

  const [carregandoOpcoes, setCarregandoOpcoes] = useState(false)
  const [erroOpcoes, setErroOpcoes] = useState('')

  useEffect(() => {
    async function carregarOpcoes() {
      if (!reserva?.quarto?.id || !reserva?.hotel?.id) {
        return
      }

      setCarregandoOpcoes(true)
      setErroOpcoes('')

      try {
        const [resTarifas, resServicos] = await Promise.all([
          fetch(
            `${API}/quartos/${reserva.quarto.id}/tarifas-temporada/`
          ),
          fetch(
            `${API}/hoteis/${reserva.hotel.id}/servicos-adicionais/`
          ),
        ])

        if (!resTarifas.ok || !resServicos.ok) {
          throw new Error(
            'Não foi possível carregar as tarifas e os serviços.'
          )
        }

        const dadosTarifas = await resTarifas.json()
        const dadosServicos = await resServicos.json()

        setTarifas(
          Array.isArray(dadosTarifas) ? dadosTarifas : []
        )

        setServicos(
          Array.isArray(dadosServicos) ? dadosServicos : []
        )
      } catch (error) {
        setErroOpcoes(error.message)
      } finally {
        setCarregandoOpcoes(false)
      }
    }

    carregarOpcoes()
  }, [reserva])

  function alternarServico(servicoId) {
    setServicosSelecionados((atuais) =>
      atuais.includes(servicoId)
        ? atuais.filter((id) => id !== servicoId)
        : [...atuais, servicoId]
    )
  }

  if (!reserva) {
    return (
      <div className="container py-4">
        <div className="alert alert-warning">
          Nenhum dado de reserva foi informado.
        </div>

        <button
          type="button"
          className="btn btn-outline-primary"
          onClick={onVoltar}
        >
          Voltar
        </button>
      </div>
    )
  }

  const {
    hotel,
    quarto,
    checkIn,
    checkOut,
    adultos,
    criancas,
  } = reserva

  // Cálculo da quantidade de diárias
  const dataEntrada = new Date(`${checkIn}T00:00:00`)
  const dataSaida = new Date(`${checkOut}T00:00:00`)

  const quantidadeDiarias = Math.round(
    (dataSaida - dataEntrada) / (1000 * 60 * 60 * 24)
  )

  // Subtotal considerando somente o preço-base do quarto
  const subtotalBase =
    Number(quarto?.preco_diaria || 0) * quantidadeDiarias

  return (
    <div className="container pb-5">

      {/* CABEÇALHO */}
      <div className="mb-4">
        <button
          type="button"
          className="btn btn-outline-secondary mb-3"
          onClick={onVoltar}
        >
          Voltar
        </button>

        <h1 className="fw-bold text-primary">
          Finalizar reserva
        </h1>

        <p className="text-secondary">
          Confira os dados da hospedagem e escolha suas opções.
        </p>
      </div>

      <div className="row g-4">

        <div className="col-lg-7">

          {/* DADOS DA HOSPEDAGEM */}
          <section className="card shadow-sm mb-4">
            <div className="card-body">

              <h2 className="h5 fw-bold mb-3">
                Dados da hospedagem
              </h2>

              <p>
                <strong>Hotel:</strong> {hotel?.nome}
              </p>

              <p>
                <strong>Quarto:</strong> {quarto?.tipo}
              </p>

              <p>
                <strong>Check-in:</strong> {checkIn}
              </p>

              <p>
                <strong>Check-out:</strong> {checkOut}
              </p>

              <p>
                <strong>Adultos:</strong> {adultos}
              </p>

              <p className="mb-0">
                <strong>Crianças:</strong> {criancas}
              </p>

            </div>
          </section>

          {/* TARIFAS */}
          <section className="card shadow-sm mb-4">
            <div className="card-body">

              <h2 className="h5 fw-bold mb-3">
                Selecione a tarifa
              </h2>

              {carregandoOpcoes ? (
                <p className="text-secondary">
                  Carregando tarifas...
                </p>
              ) : erroOpcoes ? (
                <div className="alert alert-warning">
                  {erroOpcoes}
                </div>
              ) : tarifas.length === 0 ? (
                <div className="alert alert-info">
                  Nenhuma tarifa de temporada disponível para este quarto.
                </div>
              ) : (
                <div className="list-group">

                  {tarifas.map((tarifa) => (
                    <label
                      key={tarifa.id}
                      className="list-group-item d-flex gap-2 align-items-center"
                    >
                      <input
                        type="radio"
                        name="tarifa"
                        value={tarifa.id}
                        checked={
                          tarifaSelecionada === String(tarifa.id)
                        }
                        onChange={() =>
                          setTarifaSelecionada(String(tarifa.id))
                        }
                      />

                      <span>
                        <strong>{tarifa.nome}</strong>

                        <br />

                        <small className="text-secondary">
                          {tarifa.preco_diferenciado
                            ? `Preço diferenciado: R$ ${Number(
                                tarifa.preco_diferenciado
                              ).toFixed(2)}`
                            : `Multiplicador: ${tarifa.multiplicador}`}
                        </small>
                      </span>

                    </label>
                  ))}

                </div>
              )}

            </div>
          </section>

          {/* SERVIÇOS ADICIONAIS */}
          <section className="card shadow-sm">
            <div className="card-body">

              <h2 className="h5 fw-bold mb-3">
                Serviços adicionais
              </h2>

              {carregandoOpcoes ? (
                <p className="text-secondary">
                  Carregando serviços...
                </p>
              ) : erroOpcoes ? (
                <div className="alert alert-warning">
                  {erroOpcoes}
                </div>
              ) : servicos.length === 0 ? (
                <div className="alert alert-info">
                  Nenhum serviço adicional disponível para este hotel.
                </div>
              ) : (
                <div className="list-group">

                  {servicos.map((servico) => (
                    <label
                      key={servico.id}
                      className="list-group-item d-flex align-items-center gap-2"
                    >
                      <input
                        type="checkbox"
                        checked={servicosSelecionados.includes(
                          servico.id
                        )}
                        onChange={() =>
                          alternarServico(servico.id)
                        }
                      />

                      <span>
                        <strong>{servico.nome}</strong>

                        <br />

                        <small className="text-secondary">
                          R$ {Number(servico.preco).toFixed(2)}
                          {' — '}
                          {servico.tipo_cobranca}
                        </small>
                      </span>

                    </label>
                  ))}

                </div>
              )}

            </div>
          </section>

        </div>

        {/* RESUMO DA RESERVA */}
        <div className="col-lg-5">

          <section className="card shadow-sm">
            <div className="card-body">

              <h2 className="h5 fw-bold mb-3">
                Resumo da reserva
              </h2>

              <div className="d-flex justify-content-between mb-2">
                <span>Preço da diária</span>

                <strong>
                  R$ {Number(quarto?.preco_diaria || 0).toFixed(2)}
                </strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Quantidade de diárias</span>

                <strong>
                  {quantidadeDiarias}
                </strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal base</span>

                <strong>
                  R$ {subtotalBase.toFixed(2)}
                </strong>
              </div>

              <hr />

              <div className="d-flex justify-content-between mb-2">
                <span>Tarifa selecionada</span>

                <span>
                  {tarifaSelecionada
                    ? 'Selecionada'
                    : 'Não selecionada'}
                </span>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Serviços adicionais</span>

                <span>
                  {servicosSelecionados.length} selecionado(s)
                </span>
              </div>

              <hr />

              <div className="d-flex justify-content-between">
                <strong>Total da hospedagem</strong>

                <strong className="text-primary">
                  Aguardando cálculo
                </strong>
              </div>

              <div className="alert alert-info mt-3 mb-0">
                O subtotal apresentado considera apenas o preço-base
                das diárias. O valor final depende da integração
                com o cálculo oficial do backend.
              </div>

              <button
                type="button"
                className="btn btn-primary w-100 mt-4"
                disabled
              >
                Continuar
              </button>

            </div>
          </section>

        </div>

      </div>
    </div>
  )
}