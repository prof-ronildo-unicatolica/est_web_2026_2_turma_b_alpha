import { useEffect, useState } from 'react'
import { apiFetch } from '../services/api'

function formatarData(valor) {
  if (!valor) return '-'
  const data = new Date(valor)
  if (Number.isNaN(data.getTime())) return String(valor)
  return data.toLocaleDateString('pt-BR')
}

function formatarMoeda(valor) {
  const numero = Number(valor ?? 0)
  if (Number.isNaN(numero)) return 'R$ 0,00'
  return numero.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  })
}

function badgeStatus(status) {
  const normalizado = String(status || 'Pendente').toLowerCase()
  if (normalizado.includes('confirm')) return 'bg-success'
  if (normalizado.includes('cancel')) return 'bg-danger'
  return 'bg-warning text-dark'
}

export default function MinhasReservas({ usuario, onIrLogin, onVoltarBusca }) {
  const [reservas, setReservas] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [reservaSelecionada, setReservaSelecionada] = useState(null)

  useEffect(() => {
    let ativo = true

    async function carregarReservas() {
      if (!usuario) {
        if (ativo) {
          setReservas([])
          setCarregando(false)
        }
        return
      }

      setCarregando(true)
      setErro('')

      try {
        const resposta = await apiFetch('/api/v1/reservas')

        if (!ativo) return

        if (!resposta) {
          setErro('Sessão expirada. Faça login novamente para ver suas reservas.')
          setReservas([])
          return
        }

        if (resposta.status === 404) {
          setReservas([])
          return
        }

        if (!resposta.ok) {
          throw new Error('Não foi possível carregar suas reservas.')
        }

        const dados = await resposta.json()
        const lista = Array.isArray(dados) ? dados : dados.items || dados.reservas || []
        setReservas(lista)
      } catch (err) {
        if (ativo) {
          setErro(err.message || 'Erro ao buscar reservas.')
        }
      } finally {
        if (ativo) {
          setCarregando(false)
        }
      }
    }

    carregarReservas()

    return () => {
      ativo = false
    }
  }, [usuario])

  if (!usuario) {
    return (
      <section className="bg-white rounded shadow-sm p-4">
        <h2 className="h4 fw-bold text-primary mb-2">Minhas Reservas</h2>
        <p className="text-secondary mb-3">
          Entre na sua conta para consultar suas reservas, datas, valores e status.
        </p>
        <div className="d-flex gap-2">
          <button
            type="button"
            className="btn btn-primary"
            onClick={onIrLogin}
          >
            Fazer login
          </button>
          <button
            type="button"
            className="btn btn-outline-secondary"
            onClick={onVoltarBusca}
          >
            Buscar hotéis
          </button>
        </div>
      </section>
    )
  }

  return (
    <section className="bg-white rounded shadow-sm p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="h4 fw-bold text-primary mb-1">Minhas Reservas</h2>
          <p className="text-secondary small mb-0">
            Acompanhe suas estadias, status e valores da conta.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-outline-primary btn-sm"
          onClick={onVoltarBusca}
        >
          Nova busca
        </button>
      </div>

      {erro && (
        <div className="alert alert-danger" role="alert">
          {erro}
        </div>
      )}

      {carregando ? (
        <div className="py-4 text-center text-secondary">
          Carregando suas reservas...
        </div>
      ) : reservas.length === 0 ? (
        <div className="alert alert-secondary mb-0">
          Você ainda não possui reservas registradas.
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-hover align-middle mb-0">
            <thead>
              <tr>
                <th>Hotel</th>
                <th>Período</th>
                <th>Valor</th>
                <th>Status</th>
                <th className="text-end">Ações</th>
              </tr>
            </thead>
            <tbody>
              {reservas.map((reserva, indice) => {
                const id = reserva.id ?? indice
                const nomeHotel =
                  reserva.hotel_nome ||
                  reserva.hotel?.nome ||
                  'Hotel Alpha'
                const checkIn = reserva.check_in || reserva.data_checkin
                const checkOut = reserva.check_out || reserva.data_checkout
                const valorTotal =
                  reserva.total ?? reserva.valor_total ?? reserva.preco_total
                const status = reserva.status || 'Pendente'

                return (
                  <tr key={id}>
                    <td className="fw-semibold">{nomeHotel}</td>
                    <td>
                      {formatarData(checkIn)} até {formatarData(checkOut)}
                    </td>
                    <td>{formatarMoeda(valorTotal)}</td>
                    <td>
                      <span className={`badge ${badgeStatus(status)}`}>
                        {status}
                      </span>
                    </td>
                    <td className="text-end">
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => setReservaSelecionada(reserva)}
                      >
                        Detalhes
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {reservaSelecionada && (
        <div className="border rounded bg-light p-3 mt-4">
          <div className="d-flex justify-content-between align-items-start mb-2">
            <h3 className="h6 fw-bold mb-0">
              Detalhes da reserva #{reservaSelecionada.id ?? '-'}
            </h3>
            <button
              type="button"
              className="btn-close"
              aria-label="Fechar detalhes"
              onClick={() => setReservaSelecionada(null)}
            />
          </div>
          <p className="mb-1 small">
            <strong>Hotel:</strong>{' '}
            {reservaSelecionada.hotel_nome ||
              reservaSelecionada.hotel?.nome ||
              'Hotel Alpha'}
          </p>
          <p className="mb-1 small">
            <strong>Check-in:</strong> {formatarData(reservaSelecionada.check_in)} |{' '}
            <strong>Check-out:</strong> {formatarData(reservaSelecionada.check_out)}
          </p>
          <p className="mb-1 small">
            <strong>Status:</strong> {reservaSelecionada.status || 'Pendente'}
          </p>
          <p className="mb-0 small">
            <strong>Valor total:</strong>{' '}
            {formatarMoeda(
              reservaSelecionada.total ??
                reservaSelecionada.valor_total ??
                reservaSelecionada.preco_total
            )}
          </p>
        </div>
      )}
    </section>
  )
}

