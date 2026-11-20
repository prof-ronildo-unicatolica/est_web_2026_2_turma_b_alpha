"""Testes unitarios do motor de preco (S5-03).

Estes testes dependem da funcao calcular_preco_reserva, que sera criada
pelo Kelton na issue S5-02 (app/services/reserva_service.py). Enquanto
essa funcao nao existe, os testes ficam marcados com @pytest.mark.skip.

Assim que o S5-02 for mergeado:
1. Descomentar o import abaixo.
2. Remover o decorator @pytest.mark.skip de cada teste.
3. Ajustar os nomes dos parametros/campos se a assinatura combinada
   com o Kelton for diferente da proposta.
"""

from decimal import Decimal

import pytest

# from app.services.reserva_service import calcular_preco_reserva


SKIP_REASON = "Aguardando S5-02 (reserva_service.calcular_preco_reserva)"


# --- Caso base: sem criancas, sem early/late, sem servicos, reembolsavel ---


@pytest.mark.skip(reason=SKIP_REASON)
def test_preco_base_apenas_diarias():
    """3 diarias a R$200, 2 adultos, nada mais: total = 3 * 200."""
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_preco_usa_tarifa_de_temporada_quando_informada():
    """Se valor_diaria_temporada for passado, ele substitui a base."""
    pass


# --- Criancas: bebe (0-5) gratis, crianca (6-12) a 50% ---


@pytest.mark.skip(reason=SKIP_REASON)
def test_bebe_de_0_a_5_anos_e_gratuito():
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_crianca_de_6_a_12_anos_paga_metade():
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_crianca_de_13_anos_paga_valor_cheio_de_adulto():
    """Fronteira: 13 anos ja conta como adulto, nao como crianca."""
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_fronteira_5_anos_e_gratuito_e_6_anos_paga_metade():
    """Fronteira exata entre bebe (grátis) e crianca (50%)."""
    pass


# --- Early check-in / late check-out: +30% ---


@pytest.mark.skip(reason=SKIP_REASON)
def test_early_check_in_adiciona_30_porcento():
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_late_check_out_adiciona_30_porcento():
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_early_e_late_juntos():
    """Confirmar se os 30% de cada um somam ou se e um teto unico --
    perguntar a regra exata pro Kelton antes de escrever a asserção."""
    pass


# --- Servicos adicionais: soma direta ---


@pytest.mark.skip(reason=SKIP_REASON)
def test_um_servico_adicional_e_somado_ao_total():
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_varios_servicos_adicionais_somam_corretamente():
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_sem_servicos_adicionais_nao_altera_total():
    pass


# --- Nao reembolsavel: -10%, aplicado por ultimo ---


@pytest.mark.skip(reason=SKIP_REASON)
def test_nao_reembolsavel_aplica_desconto_de_10_porcento():
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_nao_reembolsavel_e_aplicado_depois_de_criancas_e_servicos():
    """A ordem importa: o desconto de 10% deve incidir sobre o total
    ja com criancas/early-late/servicos somados, nao sobre a diaria
    base isolada."""
    pass


# --- Combinacoes e cenarios completos ---


@pytest.mark.skip(reason=SKIP_REASON)
def test_cenario_completo_com_todas_as_regras_combinadas():
    """Bebe + crianca + early + late + servico + nao reembolsavel,
    tudo junto -- serve como teste de regressao do calculo geral."""
    pass


@pytest.mark.skip(reason=SKIP_REASON)
def test_resultado_expoe_cada_componente_separadamente():
    """O retorno estruturado (ResultadoPreco) deve permitir auditar
    cada parcela do calculo, nao so o total final."""
    pass
