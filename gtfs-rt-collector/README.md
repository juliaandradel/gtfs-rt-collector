# Coleta GTFS Realtime - BH (Equipe 5 - CIN0144)

## Sobre

Script que coleta dados de atraso dos ônibus de Belo Horizonte em tempo real via API pública da BHTrans. Os dados serão cruzados com o GTFS estático para montar o dataset do projeto de Aprendizado de Máquina.

**Fonte:** Portal de Dados Abertos de BH — https://dados.pbh.gov.br/dataset/gtfs-rt

## Como funciona

A BHTrans disponibiliza uma API pública que retorna o estado atual de todos os ônibus em operação: em qual parada estão e quanto estão atrasados (em segundos). O script chama essa API a cada 3 minutos e salva os dados em CSVs (um por dia).

Cada chamada retorna ~400 registros (1 por viagem em andamento). Como cada viagem reporta apenas a próxima parada, chamadas consecutivas capturam o ônibus em paradas diferentes conforme ele avança na rota, construindo um histórico completo de delays.

Depois de alguns dias coletando, os CSVs serão cruzados com o GTFS estático pela chave `trip_id` + `stop_sequence`, formando o dataset final com features (rota, horário, coordenadas, distância) + target (delay real).

## Passo a passo

### 1. Clonar o repositório

```
git clone https://github.com/juliaandradel/gtfs-rt-collector.git
cd gtfs-rt-collector
```

### 2. Instalar dependências

```
pip install -r requirements.txt
```

### 3. Rodar o script

```
python coletor.py
```

Deve aparecer:

```
============================================================
COLETOR GTFS-RT - BH (Equipe 5)
============================================================
Intervalo: 180 segundos (3 minutos)
Dados salvos em: dados/
Para parar: Ctrl+C
============================================================

[21:00:00] Coleta #1: 408 registros | Arquivo: 0.0 MB
[21:03:00] Coleta #2: 412 registros | Arquivo: 0.1 MB
```

### 4. Configurar o PC para não suspender

- **Windows:** Configurações → Sistema → Energia → "Ao fechar a tampa" → "Não fazer nada". Mudar "Suspender após" para "Nunca".
- **Mac:** Preferências do Sistema → Economia de Energia → desmarcar suspensão automática.

### 5. Para parar

Aperta `Ctrl+C` no terminal.

### 6. Enviar dados para o repositório

```
git add dados/
git commit -m "Coleta dia XX/XX"
git push
```

Se outra pessoa já fez push antes, faça `git pull` primeiro.

### 7. Se precisar reiniciar

O script NÃO apaga dados anteriores. Pode parar e reiniciar quantas vezes quiser.

## Dados coletados

Os CSVs ficam na pasta `dados/`, um arquivo por dia:

```
dados/
  coleta_2026-04-12.csv
  coleta_2026-04-13.csv
  coleta_2026-04-14.csv
```

### Colunas

| Coluna | Descrição |
|--------|-----------|
| `timestamp_coleta` | Quando a coleta foi feita |
| `trip_id` | ID da viagem (cruza com GTFS estático) |
| `route_id` | ID da rota |
| `direction_id` | Sentido da viagem (0 ou 1) |
| `start_time` | Horário planejado de início da viagem |
| `start_date` | Data da viagem (YYYYMMDD) |
| `vehicle_id` | Número do ônibus físico |
| `vehicle_label` | Nome do veículo |
| `stop_sequence` | Posição da parada na rota (cruza com GTFS estático) |
| `stop_id` | ID da parada |
| `arrival_delay` | Atraso na chegada (segundos) — pode vir vazio |
| `departure_delay` | **TARGET** — Atraso na saída (segundos) |

### Volume esperado

- ~400 registros por chamada (1 por viagem em andamento)
- ~340 chamadas por dia (a cada 3 min, das 6h às 23h)
- ~136 mil registros brutos por dia
- ~30-50 mil registros únicos por dia (após limpeza de duplicatas)
- **Meta: coletar 5-7 dias** (incluindo dias úteis e fim de semana)

### O que são duplicatas?

O mesmo ônibus pode aparecer na mesma parada em chamadas consecutivas (ele ainda não avançou). Na limpeza, mantemos apenas 1 registro por combinação de `trip_id` + `stop_sequence` + `start_date`.

## Requisitos

- Python 3.8+
- ~30 MB de RAM
- ~230 KB de internet por chamada (a cada 3 min)
- ~30-50 MB de disco por dia