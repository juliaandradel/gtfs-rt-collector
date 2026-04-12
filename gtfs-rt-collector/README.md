# Coleta GTFS Realtime - BH (Equipe 5)

## O que é isso?

Script que coleta dados de atraso dos ônibus de BH em tempo real, via API pública da BHTrans.
Os dados coletados serão cruzados com o GTFS estático para montar o dataset do projeto de ML.

## Como funciona?

A BHTrans disponibiliza uma API que retorna, a cada consulta, o estado atual de todos os ônibus em operação: em qual parada estão e quanto estão atrasados (em segundos). O script chama essa API a cada 1 minuto e salva tudo num CSV.

## Passo a passo para rodar

### 1. Clonar o repositório
```
git clone https://github.com/SEU_USUARIO/gtfs-rt-collector.git
cd gtfs-rt-collector
```

### 2. Instalar as dependências
```
pip install gtfs-realtime-bindings requests
```

### 3. Rodar o script
```
python coletor.py
```

Vai aparecer algo assim:
```
[2026-04-10 21:00:00] Coletados 1641 registros de 1641 viagens
```

### 4. Deixar rodando
- NÃO fechar o terminal
- Pode minimizar a janela
- Pode usar o PC normalmente
- Configurar o PC para NÃO suspender:
  - **Windows**: Configurações → Sistema → Energia → "Ao fechar a tampa" → "Não fazer nada"
  - **Mac**: Preferências do Sistema → Economia de energia → desmarcar suspensão

### 5. Para parar
Aperta `Ctrl+C` no terminal.

### 6. Enviar os dados para o repositório
```
git add dados/
git commit -m "Coleta do dia XX/XX"
git push
```

### 7. Se precisar reiniciar o PC
Sem problema! Quando ligar de novo, roda `python coletor.py` novamente. 
O script NÃO apaga os dados anteriores — continua adicionando no mesmo arquivo do dia.

## Onde ficam os dados?

Na pasta `dados/`, um arquivo CSV por dia:
```
dados/
  coleta_2026-04-10.csv
  coleta_2026-04-11.csv
  coleta_2026-04-12.csv
```

## O que cada coluna significa?

| Coluna | Descrição |
|--------|-----------|
| timestamp_coleta | Quando a coleta foi feita |
| trip_id | ID da viagem (cruza com GTFS estático) |
| route_id | ID da rota |
| direction_id | Sentido da viagem (0 ou 1) |
| start_time | Horário planejado de início da viagem |
| start_date | Data da viagem (YYYYMMDD) |
| vehicle_id | Número do ônibus físico |
| vehicle_label | Nome do veículo |
| stop_sequence | Posição da parada na rota |
| stop_id | ID da parada (cruza com GTFS estático) |
| arrival_delay | Atraso na chegada (segundos) |
| departure_delay | **TARGET** - Atraso na saída (segundos) |

## Meta de coleta

- **Mínimo**: 3 dias
- **Ideal**: 5-7 dias (incluindo dias úteis e fim de semana)
- **Quanto mais, melhor!**

Cada dia gera ~200-500 mil registros únicos após limpeza de duplicatas.
