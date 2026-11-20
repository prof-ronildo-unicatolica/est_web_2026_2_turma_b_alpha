import { useCallback, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export function MinhasReservasLista({ token, reloadKey = 0 }) {
  const [reservas, setReservas] = useState([]);
  const [filtroStatus, setFiltroStatus] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);

  const carregarReservas = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const qs = filtroStatus ? `?status=${encodeURIComponent(filtroStatus)}` : "";
      const resp = await fetch(`${API_BASE}/api/v1/reservas${qs}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail ?? "Erro ao carregar reservas.");
      }
      const dados = await resp.json();
      setReservas(dados);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao listar reservas.");
    } finally {
      setCarregando(false);
    }
  }, [filtroStatus, token]);

  useEffect(() => {
    carregarReservas();
  }, [carregarReservas, reloadKey]);

  return (
    <div>
      <div>
        <label htmlFor="filtro-status-reserva">Filtrar por status: </label>
        <select
          id="filtro-status-reserva"
          value={filtroStatus}
          onChange={(e) => setFiltroStatus(e.target.value)}
        >
          <option value="">Todos</option>
          <option value="PENDENTE">PENDENTE</option>
          <option value="CONFIRMADA">CONFIRMADA</option>
          <option value="REJEITADA">REJEITADA</option>
          <option value="CANCELADA">CANCELADA</option>
        </select>
        <button type="button" onClick={carregarReservas} disabled={carregando}>
          {carregando ? "Atualizando..." : "Atualizar lista"}
        </button>
      </div>

      {erro && <p role="alert">{erro}</p>}

      <ul>
        {reservas.map((item) => (
          <li key={item.id}>
            <strong>{item.status}</strong> — {item.check_in} a {item.check_out} — R${" "}
            {item.valor_total}
            {item.motivo_rejeicao ? ` (${item.motivo_rejeicao})` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}