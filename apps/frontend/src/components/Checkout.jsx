import { useEffect, useMemo, useState } from 'react'
import { apiFetch } from '../services/api'

const API = 'http://localhost:8000/api/v1'

function formatarMoeda(valor) {
  const numero = Number(valor ?? 0)
  return `R$ ${Number.isFinite(numero) ? numero.toFixed(2) : '0.00'}`
}

export default function Checkout({ reserva, onVoltar }) {
  const [checkIn, setCheckIn] = useState(reserva?.checkIn || '')
  const [checkOut, setCheckOut] = useState(reserva?.checkOut || '')
  const [idadesHospedes, setIdadesHospedes] = useState(() => {
    const qtdAdultos = Math.max(1, Number(reserva?.adultos || 1))
    const qtdCriancas = Math.max(0, Number(reserva?.criancas || 0))
    return [
      ...Array.from({ length: qtdAdultos }, () => 30),
      ...Array.from({ length: qtdCriancas }, () => 8),
    ]
  })

  const [tarifaSelecionada, setTarifaSelecionada] = useState('')
  const [servicosSelecionados, setServicosSelecionados] = useState([])
  const [earlyCheckIn, setEarlyCheckIn] = useState(false)
  const [lateCheckOut, setLateCheckOut] = useState(false)
  const [naoReembolsavel, setNaoReembolsavel] = useState(false)

  const [tarifas, setTarifas] = useState([])
  const [servicos, setServicos] = useState([])
  const [carregandoOpcoes, setCarregandoOpcoes] = useState(false)
  const [erroOpcoes, setErroOpcoes] = useState('')

  const [preview, setPreview] = useState(null)
  const [carregandoPreview, setCarregandoPreview] = useState(false)
  const [erroPreview, setErroPreview] = useState('')

  useEffect(() => {
    setCheckIn(reserva?.checkIn || '')
    setCheckOut(reserva?.checkOut || '')
    const qtdAdultos = Math.max(1, Number(reserva?.adultos || 1))
    const qtdCriancas = Math.max(0, Number(reserva?.criancas || 0))
    setIdadesHospedes([
      ...Array.from({ length: qtdAdultos }, () => 30),
      ...Array.from({ length: qtdCriancas }, () => 8),
    ])
    setTarifaSelecionada('')
    setServicosSelecionados([])
    setEarlyCheckIn(false)
    setLateCheckOut(false)
    setNaoReembolsavel(false)
    setPreview(null)
    setErroPreview('')
  }, [reserva])

  useEffect(() => {
    async function carregarOpcoes() {
      if (!reserva?.quarto?.id || !reserva?.hotel?.id) {
        return
      }

      setCarregandoOpcoes(true)
      setErroOpcoes('')

      try {
        const [resTarifas, resServicos] = await Promise.all([
          apiFetch(`/quartos/${reserva.quarto.id}/tarifas-temporada/`),
          apiFetch(`/hoteis/${reserva.hotel.id}/servicos-adicionais/`),
        ])

        if (!resTarifas || !resServicos || !resTarifas.ok || !resServicos.ok) {
          throw new Error(
            'Não foi possível carregar as tarifas e os serviços.'
          )
        }

        const dadosTarifas = await resTarifas.json()
        const dadosServicos = await resServicos.json()

        setTarifas(Array.isArray(dadosTarifas) ? dadosTarifas : [])
        setServicos(Array.isArray(dadosServicos) ? dadosServicos : [])
      } catch (error) {
        setErroOpcoes(error.message)
      } finally {
        setCarregandoOpcoes(false)
      }
    }

    carregarOpcoes()
  }, [reserva])

  const payloadPreview = useMemo(() => {
    if (!reserva?.quarto?.id || !checkIn || !checkOut) {
      return null
    }
    const idadesLimpias = idadesHospedes
      .map((idade) => Number(idade))
      .filter((idade) => Number.isFinite(idade) && idade >= 0)

    if (idadesLimpias.length === 0) {
      return null
    }

    return {
      quarto_id: reserva.quarto.id,
      check_in: checkIn,
      check_out: checkOut,
      hospedes_idades: idadesLimpias,
      servicos_adicionais_ids: servicosSelecionados,
      early_check_in: earlyCheckIn,
      late_check_out: lateCheckOut,
      nao_reembolsavel: naoReembolsavel,
    }
  }, [
    reserva,
    checkIn,
    checkOut,
    idadesHospedes,
    servicosSelecionados,
    earlyCheckIn,
    lateCheckOut,
    naoReembolsavel,
  ])

  useEffect(() => {
    let ativo = true

    async function buscarPreview() {
      if (!payloadPreview) {
        setPreview(null)
        setErroPreview('')
        return
      }

      if (payloadPreview.check_out <= payloadPreview.check_in) {
        setPreview(null)
        setErroPreview('A data de check-out deve ser posterior ao check-in.')
        return
      }

      setCarregandoPreview(true)
      setErroPreview('')

      try {
        const resposta = await fetch(`${API}/reservas/preview`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payloadPreview),
        })

        const corpo = await resposta.json().catch(() => ({}))

        if (!ativo) return

        if (!resposta.ok) {
          const mensagemErro =
            typeof corpo?.detail === 'string'
              ? corpo.detail
              : Array.isArray(corpo?.detail)
                ? corpo.detail.map((item) => item.msg).join('; ')
                : 'Não foi possível calcular o preview da reserva.'
          setPreview(null)
          setErroPreview(mensagemErro)
          return
        }

        setPreview(corpo)
      } catch {
        if (!ativo) return
        setPreview(null)
        setErroPreview('Erro de comunicação ao calcular o preview.')
      } finally {
        if (ativo) {
          setCarregandoPreview(false)
        }
      }
    }

    buscarPreview()

    return () => {
      ativo = false
    }
  }, [payloadPreview])

  function alternarServico(servicoId) {
    setServicosSelecionados((atuais) =>
      atuais.includes(servicoId)
        ? atuais.filter((id) => id !== servicoId)
        : [...atuais, servicoId]
    )
  }

  function atualizarIdadeHospede(indice, valor) {
    const numero = Number(valor)
    setIdadesHospedes((atuais) =>
      atuais.map((item, idx) => (idx === indice ? numero : item))
    )
  }

  function adicionarHospede(idadePadrao = 30) {
    setIdadesHospedes((atuais) => [...atuais, idadePadrao])
  }

  function removerHospede(indice) {
    setIdadesHospedes((atuais) =>
      atuais.length > 1 ? atuais.filter((_, idx) => idx !== indice) : atuais
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

  const { hotel, quarto } = reserva

  return (
    <div className="container pb-5">
      <div className="mb-4">
        <button
          type="button"
          className="btn btn-outline-secondary mb-3"
          onClick={onVoltar}
        >
          Voltar
        </button>

        <h1 className="fw-bold text-primary">Finalizar reserva</h1>

        <p className="text-secondary">
          Confira os dados da hospedagem e escolha suas opções.
        </p>
      </div>

      <div className="row g-4">
        <div className="col-lg-7">
          <section className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="h5 fw-bold mb-3">Dados da hospedagem</h2>

              <p>
                <strong>Hotel:</strong> {hotel?.nome}
              </p>

              <p>
                <strong>Quarto:</strong> {quarto?.tipo}
              </p>

              <div className="row g-3 mb-3">
                <div className="col-sm-6">
                  <label className="form-label fw-semibold">Check-in</label>
                  <input
                    type="date"
                    className="form-control"
                    value={checkIn}
                    onChange={(e) => setCheckIn(e.target.value)}
                  />
                </div>
                <div className="col-sm-6">
                  <label className="form-label fw-semibold">Check-out</label>
                  <input
                    type="date"
                    className="form-control"
                    value={checkOut}
                    onChange={(e) => setCheckOut(e.target.value)}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span className="fw-semibold">
                    Idades dos hóspedes ({idadesHospedes.length})
                  </span>
                  <div className="d-flex gap-2">
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => adicionarHospede(30)}
                    >
                      + Adulto
                    </button>
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-secondary"
                      onClick={() => adicionarHospede(8)}
                    >
                      + Criança
                    </button>
                  </div>
                </div>

                <div className="row g-2">
                  {idadesHospedes.map((idade, idx) => (
                    <div key={idx} className="col-6 col-md-4 d-flex gap-1">
                      <input
                        type="number"
                        min={0}
                        max={120}
                        className="form-control form-control-sm"
                        value={idade}
                        onChange={(e) =>
                          atualizarIdadeHospede(idx, e.target.value)
                        }
                        aria-label={`Idade do hóspede ${idx + 1}`}
                      />
                      {idadesHospedes.length > 1 && (
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => removerHospede(idx)}
                          title="Remover hóspede"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}
                </div>
                <small className="text-muted d-block mt-1">
                  0–5 anos: gratuito | 6–12 anos: 50% | acima de 12: adulto.
                </small>
              </div>

              <div className="d-flex flex-wrap gap-3">
                <label className="form-check-label d-flex align-items-center gap-2">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    checked={earlyCheckIn}
                    onChange={(e) => setEarlyCheckIn(e.target.checked)}
                  />
                  Early check-in (+30%)
                </label>

                <label className="form-check-label d-flex align-items-center gap-2">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    checked={lateCheckOut}
                    onChange={(e) => setLateCheckOut(e.target.checked)}
                  />
                  Late check-out (+30%)
                </label>

                <label className="form-check-label d-flex align-items-center gap-2">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    checked={naoReembolsavel}
                    onChange={(e) => setNaoReembolsavel(e.target.checked)}
                  />
                  Tarifa não reembolsável (-10%)
                </label>
              </div>
            </div>
          </section>

          <section className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="h5 fw-bold mb-3">Selecione a tarifa</h2>

              {carregandoOpcoes ? (
                <p className="text-secondary">Carregando tarifas...</p>
              ) : erroOpcoes ? (
                <div className="alert alert-warning">{erroOpcoes}</div>
              ) : tarifas.length === 0 ? (
                <div className="alert alert-info">
                  Nenhuma tarifa de temporada cadastrada para este quarto (o
                  motor aplica automaticamente se houver vigência no período).
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
                        checked={tarifaSelecionada === String(tarifa.id)}
                        onChange={() =>
                          setTarifaSelecionada(String(tarifa.id))
                        }
                      />

                      <span>
                        <strong>{tarifa.nome}</strong>
                        <br />
                        <small className="text-secondary">
                          {tarifa.preco_diferenciado
                            ? `Preço diferenciado: ${formatarMoeda(tarifa.preco_diferenciado)}`
                            : `Multiplicador: ${tarifa.multiplicador}`}
                        </small>
                      </span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </section>

          <section className="card shadow-sm">
            <div className="card-body">
              <h2 className="h5 fw-bold mb-3">Serviços adicionais</h2>

              {carregandoOpcoes ? (
                <p className="text-secondary">Carregando serviços...</p>
              ) : erroOpcoes ? (
                <div className="alert alert-warning">{erroOpcoes}</div>
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
                        checked={servicosSelecionados.includes(servico.id)}
                        onChange={() => alternarServico(servico.id)}
                      />

                      <span>
                        <strong>{servico.nome}</strong>
                        <br />
                        <small className="text-secondary">
                          {formatarMoeda(servico.preco)} — {servico.tipo_cobranca}
                        </small>
                      </span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>

        <div className="col-lg-5">
          <section className="card shadow-sm">
            <div className="card-body">
              <h2 className="h5 fw-bold mb-3">Resumo da reserva</h2>

              <div className="d-flex justify-content-between mb-2">
                <span>Preço da diária</span>
                <strong>{formatarMoeda(quarto?.preco_diaria)}</strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Quantidade de diárias</span>
                <strong>{preview?.quantidade_diarias ?? '-'}</strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal das diárias</span>
                <strong>
                  {preview ? formatarMoeda(preview.subtotal_diarias) : '-'}
                </strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Adicional de hóspedes</span>
                <strong>
                  {preview ? formatarMoeda(preview.adicional_hospedes) : '-'}
                </strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Early / Late check-in/out</span>
                <strong>
                  {preview ? formatarMoeda(preview.adicional_early_late) : '-'}
                </strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Serviços adicionais</span>
                <strong>
                  {preview ? formatarMoeda(preview.total_servicos) : '-'}
                </strong>
              </div>

              <div className="d-flex justify-content-between mb-2">
                <span>Desconto não reembolsável</span>
                <strong>
                  {preview
                    ? `-${formatarMoeda(preview.desconto_nao_reembolsavel)}`
                    : '-'}
                </strong>
              </div>

              <hr />

              <div className="d-flex justify-content-between">
                <strong>Total da hospedagem</strong>
                <strong className="text-primary">
                  {carregandoPreview
                    ? 'Calculando...'
                    : preview
                      ? formatarMoeda(preview.total)
                      : 'Aguardando cálculo'}
                </strong>
              </div>

              {erroPreview && (
                <div className="alert alert-danger mt-3 mb-0">{erroPreview}</div>
              )}

              <button
                type="button"
                className="btn btn-primary w-100 mt-4"
                disabled={!preview || carregandoPreview}
              >
                Continuar para reserva (Sprint 6)
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}