import { useEffect, useState } from 'react'
import { ReservaAsyncPanel } from './ReservaAsyncPanel'
import { MinhasReservasLista } from './MinhasReservasLista'

export function ReservasPage({ tokenProp, reservaInicial = null, onVoltar }) {
  const token =
    tokenProp ??
    localStorage.getItem('access_token') ??
    ''

  const [quartoId, setQuartoId] = useState('40db7253-1956-419a-999c-f52a7134e0d4')
  const [checkIn, setCheckIn] = useState('2026-12-25')
  const [checkOut, setCheckOut] = useState('2026-12-27')
  const [idadesTexto, setIdadesTexto] = useState('30, 28')
  const [earlyCheckIn, setEarlyCheckIn] = useState(false)
  const [lateCheckOut, setLateCheckOut] = useState(false)
  const [naoReembolsavel, setNaoReembolsavel] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (!reservaInicial) return
    if (reservaInicial.quarto_id) setQuartoId(String(reservaInicial.quarto_id))
    if (reservaInicial.check_in) setCheckIn(String(reservaInicial.check_in))
    if (reservaInicial.check_out) setCheckOut(String(reservaInicial.check_out))
    if (Array.isArray(reservaInicial.hospedes_idades) && reservaInicial.hospedes_idades.length > 0) {
      setIdadesTexto(reservaInicial.hospedes_idades.join(', '))
    }
    if (typeof reservaInicial.early_check_in === 'boolean') {
      setEarlyCheckIn(reservaInicial.early_check_in)
    }
    if (typeof reservaInicial.late_check_out === 'boolean') {
      setLateCheckOut(reservaInicial.late_check_out)
    }
    if (typeof reservaInicial.nao_reembolsavel === 'boolean') {
      setNaoReembolsavel(reservaInicial.nao_reembolsavel)
    }
  }, [reservaInicial])

  const hospedesIdades = idadesTexto
    .split(',')
    .map((v) => Number(v.trim()))
    .filter((n) => !Number.isNaN(n) && n >= 0)

  const payload = {
    quarto_id: quartoId.trim(),
    check_in: checkIn,
    check_out: checkOut,
    hospedes_idades: hospedesIdades.length > 0 ? hospedesIdades : [30],
    servicos_adicionais_ids: [],
    early_check_in: earlyCheckIn,
    late_check_out: lateCheckOut,
    nao_reembolsavel: naoReembolsavel,
  }

  return (
    <div className="card shadow-sm p-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2 className="h4 mb-0">Reservas Assíncronas</h2>
        {onVoltar && (
          <button
            type="button"
            className="btn btn-outline-secondary btn-sm"
            onClick={onVoltar}
          >
            Voltar
          </button>
        )}
      </div>

      <div className="row g-3 mb-3">
        <div className="col-md-6">
          <label className="form-label">ID do Quarto</label>
          <input
            type="text"
            className="form-control"
            value={quartoId}
            onChange={(e) => setQuartoId(e.target.value)}
          />
        </div>

        <div className="col-md-3">
          <label className="form-label">Check-in</label>
          <input
            type="date"
            className="form-control"
            value={checkIn}
            onChange={(e) => setCheckIn(e.target.value)}
          />
        </div>

        <div className="col-md-3">
          <label className="form-label">Check-out</label>
          <input
            type="date"
            className="form-control"
            value={checkOut}
            onChange={(e) => setCheckOut(e.target.value)}
          />
        </div>

        <div className="col-md-6">
          <label className="form-label">Idades dos hóspedes (separadas por vírgula)</label>
          <input
            type="text"
            className="form-control"
            value={idadesTexto}
            onChange={(e) => setIdadesTexto(e.target.value)}
          />
        </div>

        <div className="col-md-6 d-flex align-items-end gap-3">
          <div className="form-check">
            <input
              id="earlyCheckIn"
              type="checkbox"
              className="form-check-input"
              checked={earlyCheckIn}
              onChange={(e) => setEarlyCheckIn(e.target.checked)}
            />
            <label htmlFor="earlyCheckIn" className="form-check-label">
              Early check-in
            </label>
          </div>

          <div className="form-check">
            <input
              id="lateCheckOut"
              type="checkbox"
              className="form-check-input"
              checked={lateCheckOut}
              onChange={(e) => setLateCheckOut(e.target.checked)}
            />
            <label htmlFor="lateCheckOut" className="form-check-label">
              Late check-out
            </label>
          </div>

          <div className="form-check">
            <input
              id="naoReembolsavel"
              type="checkbox"
              className="form-check-input"
              checked={naoReembolsavel}
              onChange={(e) => setNaoReembolsavel(e.target.checked)}
            />
            <label htmlFor="naoReembolsavel" className="form-check-label">
              Não reembolsável
            </label>
          </div>
        </div>
      </div>

      <ReservaAsyncPanel
        token={token}
        payload={payload}
        onFinalStatus={() => setReloadKey((k) => k + 1)}
      />

      <hr className="my-4" />

      <h3 className="h5 mb-3">Minhas Reservas</h3>
      <MinhasReservasLista token={token} reloadKey={reloadKey} />
    </div>
  )
}