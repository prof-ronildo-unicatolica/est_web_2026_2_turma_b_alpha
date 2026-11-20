import asyncio
import json
import uuid
from datetime import datetime, timezone

import aio_pika
from sqlalchemy import and_, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.rabbitmq import publish_event
from app.models.quarto import Quarto
from app.models.reserva import Reserva, StatusReserva

FILA_SOLICITACOES_RESERVA = "solicitacoes-reserva"
FILA_AUDITORIA = "audit.logs"


def _processar_reserva_sync(reserva_id_str: str) -> dict:
    db = SessionLocal()
    try:
        try:
            reserva_id = uuid.UUID(reserva_id_str)
        except ValueError:
            return {"status": "IGNORADA", "motivo": "reserva_id invalido"}

        reserva = db.scalar(select(Reserva).where(Reserva.id == reserva_id))
        if reserva is None:
            return {"status": "IGNORADA", "motivo": "reserva nao encontrada"}

        if reserva.status != StatusReserva.PENDENTE:
            return {
                "status": reserva.status.value,
                "motivo": "reserva ja processada anteriormente",
            }

        quarto = db.scalar(select(Quarto).where(Quarto.id == reserva.quarto_id))
        if quarto is None:
            reserva.status = StatusReserva.REJEITADA
            reserva.motivo_rejeicao = "Quarto nao encontrado."
        else:
            conflito = db.scalar(
                select(Reserva.id).where(
                    and_(
                        Reserva.quarto_id == reserva.quarto_id,
                        Reserva.id != reserva.id,
                        Reserva.status == StatusReserva.CONFIRMADA,
                        Reserva.check_in < reserva.check_out,
                        Reserva.check_out > reserva.check_in,
                    )
                )
            )

            if conflito is not None:
                reserva.status = StatusReserva.REJEITADA
                reserva.motivo_rejeicao = "Quarto indisponivel no periodo solicitado."
            else:
                reserva.status = StatusReserva.CONFIRMADA
                reserva.motivo_rejeicao = None

        reserva.atualizado_em = datetime.now(timezone.utc)
        db.commit()
        db.refresh(reserva)

        return {
            "reserva_id": str(reserva.id),
            "usuario_id": str(reserva.usuario_id),
            "quarto_id": str(reserva.quarto_id),
            "status": reserva.status.value,
            "motivo_rejeicao": reserva.motivo_rejeicao,
            "valor_total": str(reserva.valor_total),
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        payload = json.loads(message.body.decode("utf-8"))
        reserva_id = str(payload.get("reserva_id", ""))
        print(f"[ReservaWorker] Processando solicitacao: {payload}")

        resultado = await asyncio.to_thread(_processar_reserva_sync, reserva_id)
        print(f"[ReservaWorker] Resultado: {resultado}")

        if resultado.get("reserva_id"):
            evento_auditoria = {
                "evento": f"RESERVA_{resultado['status']}",
                **resultado,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await publish_event(FILA_AUDITORIA, evento_auditoria)


async def main():
    print(f"[ReservaWorker] Conectando ao RabbitMQ: {settings.RABBITMQ_URL}")
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(FILA_SOLICITACOES_RESERVA, durable=True)

        print(
            f"[ReservaWorker] Aguardando mensagens na fila '{FILA_SOLICITACOES_RESERVA}'..."
        )
        await queue.consume(process_message)
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[ReservaWorker] Parado pelo usuario.")
