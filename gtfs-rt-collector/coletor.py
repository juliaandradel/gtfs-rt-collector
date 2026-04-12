"""
=============================================================
SCRIPT DE COLETA DE DADOS GTFS REALTIME - BH
Equipe 5 - CIN0144
=============================================================

O QUE FAZ:
  Chama a API publica da BHTrans a cada 3 minutos e salva os
  dados de atraso de todos os onibus em operacao num CSV.
  Cada chamada retorna ~400 registros (1 por viagem em andamento).
  Ao longo do dia, captura cada onibus em diferentes paradas,
  construindo um historico de delays reais.

COMO RODAR:
  1. pip install gtfs-realtime-bindings requests
  2. python coletor.py

COMO PARAR:
  Ctrl+C no terminal

OS DADOS SAO SALVOS EM:
  pasta dados/ (um arquivo por dia)
"""

from google.transit import gtfs_realtime_pb2
import requests
import csv
import time
import os
from datetime import datetime


# =============================================================
# CONFIGURACAO
# =============================================================

# URL da API publica da BHTrans (Portal de Dados Abertos de BH)
# Cada chamada retorna o estado atual de todos os onibus
# Fonte: https://dados.pbh.gov.br/dataset/gtfs-rt
URL = "http://realtime4.mobilibus.com/web/4ch6j/trip-updates?accesskey=982a57efd77a9462bf1665696fb25984"

# Pasta onde os CSVs serao salvos
PASTA_DADOS = "dados"

# Intervalo entre coletas (em segundos)
# 180 = a cada 3 minutos
# Justificativa: cada viagem reporta 1 parada por chamada.
# A cada 3 min, o onibus avanca ~1-2 paradas, permitindo
# capturar ~20-25 paradas por viagem ao longo da rota.
INTERVALO = 180


# =============================================================
# FUNCOES
# =============================================================

def criar_pasta():
    """Cria a pasta de dados se nao existir."""
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)
        print(f"Pasta '{PASTA_DADOS}/' criada.")


def nome_arquivo_hoje():
    """
    Retorna o nome do arquivo CSV do dia atual.
    Cada dia gera um arquivo separado para facilitar o controle.
    Ex: dados/coleta_2026-04-10.csv
    """
    hoje = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(PASTA_DADOS, f"coleta_{hoje}.csv")


def criar_cabecalho(arquivo):
    """Cria o arquivo CSV com o cabecalho (nomes das colunas) se nao existir."""
    if not os.path.exists(arquivo):
        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp_coleta",    # Quando essa coleta foi feita (ex: 2026-04-10 21:00:00)
                "trip_id",             # ID da viagem - CHAVE para cruzar com GTFS estatico
                "route_id",            # ID da rota (ex: SC02A, 9201)
                "direction_id",        # Sentido da viagem (0 = ida, 1 = volta)
                "start_time",          # Horario planejado de inicio da viagem (ex: 17:11:00)
                "start_date",          # Data da viagem (ex: 20260410)
                "vehicle_id",          # Numero do onibus fisico (ex: 21301)
                "vehicle_label",       # Nome/apelido do veiculo (ex: Santa Efigenia)
                "stop_sequence",       # Posicao da parada na rota - CHAVE para cruzar com GTFS estatico
                "stop_id",             # ID da parada (ex: 14790427)
                "arrival_delay",       # Atraso na chegada em segundos (pode vir vazio)
                "departure_delay"      # Atraso na saida em segundos - ESTE EH O TARGET DO MODELO
            ])
        print(f"Arquivo criado: {arquivo}")


def coletar_uma_vez():
    """
    Faz UMA chamada a API e salva os dados no CSV do dia.

    A API retorna um 'feed' com todas as viagens em andamento naquele
    momento. Cada viagem reporta 1 parada (a proxima) com o delay em
    segundos. Chamadas consecutivas capturam o onibus em paradas
    diferentes conforme ele avanca na rota.

    Retorna: (numero de registros salvos, numero de viagens no feed)
    """
    # Garantir que a pasta e o arquivo existem
    criar_pasta()
    arquivo = nome_arquivo_hoje()
    criar_cabecalho(arquivo)

    # Chamar a API da BHTrans
    # A resposta vem em formato protobuf (binario compacto do Google)
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(URL, timeout=30)
    feed.ParseFromString(response.content)

    # Horario desta coleta
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registros = 0

    # Abrir o CSV em modo "a" (append = adiciona no final, nao apaga)
    with open(arquivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Percorrer todas as viagens em andamento
        # Cada "entity" eh um onibus rodando agora em BH
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                tu = entity.trip_update

                # Dados da viagem (extraidos do feed em tempo real)
                trip_id = tu.trip.trip_id
                route_id = tu.trip.route_id
                direction_id = tu.trip.direction_id
                start_time = tu.trip.start_time
                start_date = tu.trip.start_date

                # Dados do veiculo fisico
                vehicle_id = tu.vehicle.id if tu.HasField('vehicle') else ""
                vehicle_label = tu.vehicle.label if tu.HasField('vehicle') else ""

                # Percorrer as paradas com informacao de atraso
                # (BH geralmente reporta 1 parada por viagem - a proxima)
                for stu in tu.stop_time_update:
                    arr_delay = stu.arrival.delay if stu.HasField('arrival') else ""
                    dep_delay = stu.departure.delay if stu.HasField('departure') else ""

                    writer.writerow([
                        timestamp, trip_id, route_id, direction_id,
                        start_time, start_date, vehicle_id, vehicle_label,
                        stu.stop_sequence, stu.stop_id, arr_delay, dep_delay
                    ])
                    registros += 1

    return registros, len(feed.entity)


# =============================================================
# EXECUCAO - LOOP CONTINUO
# =============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("COLETOR GTFS-RT - BH (Equipe 5)")
    print("=" * 60)
    print(f"Intervalo: {INTERVALO} segundos ({INTERVALO//60} minutos)")
    print(f"Dados salvos em: {PASTA_DADOS}/")
    print(f"Para parar: Ctrl+C")
    print("=" * 60)
    print()

    coleta_num = 0

    while True:
        try:
            registros, entidades = coletar_uma_vez()
            coleta_num += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            arquivo = nome_arquivo_hoje()
            
            # Mostrar tamanho do arquivo atual
            tamanho_mb = os.path.getsize(arquivo) / (1024 * 1024)
            print(f"[{timestamp}] Coleta #{coleta_num}: {registros} registros | Arquivo: {tamanho_mb:.1f} MB")

        except KeyboardInterrupt:
            print(f"\n\nColeta encerrada. Total: {coleta_num} coletas realizadas.")
            print(f"Dados salvos em: {PASTA_DADOS}/")
            break

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRO: {e}")

        # Esperar antes da proxima coleta
        time.sleep(INTERVALO)