import { useCallback, useEffect, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const ESTADOS_FINAIS = new Set(["CONFIRMADA", "REJEITADA", "CANCELADA"]);
const MAX_TENTATIVAS = 20;

export function ReservaAsyncPanel({
  token,
  payload,
  intervalMs = 1500,
  onFinalStatus,
}) {
  const [reserva, setReserva] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const [consultando, setConsultando] = useState(false);
  const [erro, setErro] = useState(null);
  const timerRef = useRef(null);
  const tentativasRef = useRef(0);

  const pararPolling = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    tentativasRef.current = 0;
    setConsultando(false);
  }, []);

  useEffect(() => () => pararPolling(), [pararPolling]);

  const consultarPorId = useCallback(
    async (reservaId) => {
      const resp = await fetch(`${API_BASE}/api/v1/reservas/${reservaId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail ?? `Erro ao consultar reserva (${resp.status}).`);
      }
      return resp.json();
    },
    [token]
  );

  const handleSolicitar = async () => {
    pararPolling();
    setEnviando(true);
    setErro(null);

    try {
      const resp = await fetch(`${API_BASE}/api/v1/reservas`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail ?? `Erro ao criar reserva (${resp.status}).`);
      }

      const criada = await resp.json();
      setReserva(criada);

      if (ESTADOS_FINAIS.has(criada.status)) {
        onFinalStatus?.(criada);
        return;
      }

      setConsultando(true);
      timerRef.current = window.setInterval(async () => {
        tentativasRef.current += 1;

        try {
          const atual = await consultarPorId(criada.id);
          setReserva(atual);

          if (ESTADOS_FINAIS.has(atual.status)) {
            pararPolling();
            onFinalStatus?.(atual);
            return;
          }

          if (tentativasRef.current >= MAX_TENTATIVAS) {
            pararPolling();
            setErro(
              "A reserva ainda esta em processamento. Atualize a lista em instantes."
            );
          }
        } catch (pollErr) {
          pararPolling();
          setErro(
            pollErr instanceof Error
              ? pollErr.message
              : "Falha ao acompanhar o status da reserva."
          );
        }
      }, intervalMs);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao solicitar reserva.");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div>
      <button type="button" onClick={handleSolicitar} disabled={enviando || consultando}>
        {enviando
          ? "Enviando solicitacao..."
          : consultando
          ? "Processando reserva..."
          : "Confirmar solicitacao de reserva"}
      </button>

      {erro && <p role="alert">{erro}</p>}

      {reserva && (
        <div>
          <p>
            <strong>Codigo:</strong> {reserva.id}
          </p>
          <p>
            <strong>Status:</strong> {reserva.status}
            {consultando && reserva.status === "PENDENTE"
              ? " (validando disponibilidade no worker...)"
              : ""}
          </p>
          <p>
            <strong>Valor total:</strong> R$ {reserva.valor_total}
          </p>
          {reserva.status === "REJEITADA" && reserva.motivo_rejeicao && (
            <p role="alert">
              <strong>Motivo da rejeicao:</strong> {reserva.motivo_rejeicao}
            </p>
          )}
        </div>
      )}
    </div>
  );
}