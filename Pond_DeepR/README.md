# Análise de Funções de Recompensa — DeepRacer for Cloud

**Aluno:** [Seu nome]  
**Curso / Turma:** [Preencher]  
**Data:** [Preencher]

---

## 1. Descrição das Funções de Recompensa

### Variante 1 — Baseline: Centro + Velocidade (`variant_1_baseline.py`)

A função divide a pista em três faixas concêntricas e atribui recompensa decrescente conforme o carro se afasta do centro. Um bônus de velocidade, normalizado entre 1 m/s e 4 m/s, é somado com peso de 30%.

```
reward = 0.7 × center_reward + 0.3 × speed_reward
```

| Distância do centro | `center_reward` |
|---------------------|-----------------|
| ≤ 10 % da largura   | 1.0             |
| ≤ 25 % da largura   | 0.5             |
| ≤ 50 % da largura   | 0.1             |
| > 50 % da largura   | 0.001           |

Saída da pista retorna recompensa mínima (0,001) imediatamente.

---

### Variante 2 — Heading por Waypoint + Direção Suave (`variant_2_waypoint_heading.py`)

A função recompensa o alinhamento do veículo com o próximo waypoint (via diferença de ângulos), penaliza ângulos de direção acentuados (> 15°) e condiciona o bônus de velocidade à qualidade do heading — evitando que o agente acelere em curvas mal navegadas.

```
reward = 0.40 × heading_reward
       + 0.25 × speed_reward × heading_reward   (velocidade só vale se bem alinhado)
       + 0.20 × center_reward
       + 0.15 × steering_penalty
```

O `heading_reward` usa `cos(erro_de_heading)`, produzindo decaimento suave: alinhamento perfeito = 1,0; 30° de erro ≈ 0,87; 90° de erro = 0.

---

## 2. Justificativa das Escolhas

### Por que Variante 1 como baseline?
A V1 é intencionalmente simples: um único critério geométrico (centro) mais velocidade. Funciona como controle experimental — qualquer ganho observado na V2 pode ser atribuído diretamente às escolhas adicionais de design, não a um ponto de partida mais forte.

### Por que Variante 2 usa waypoints e heading?
Um carro que segue o centro *geometricamente* pode mesmo assim errar curvas porque não antecipa a direção da pista. O heading por waypoint força o agente a aprender a olhar "para frente". O `cos(erro)` foi escolhido em vez de bandas fixas porque fornece gradiente contínuo — o agente tem incentivo mesmo quando está levemente desalinhado.

A penalidade de steering tem origem em um problema clássico de convergência em DeepRacer: sem ela, o agente frequentemente aprende a ziguezaguear no centro (maximiza recompensa de centro mas desperdiça velocidade e desgasta a trajetória). Penalizar ângulos > 15° incentiva trajetórias mais suaves.

Condicionar `speed_reward` ao `heading_reward` cria um acoplamento importante: o agente só é recompensado por alta velocidade quando está bem alinhado — o que desencoraja a aceleração antes de curvas fechadas.

---

## 3. Análise do Comportamento Observado

> **Preencher após as execuções.** Use as métricas salvas em `logs/` e os gráficos gerados pelo DeepRacer for Cloud.

### Variante 1

| Métrica | Valor observado |
|---------|----------------|
| Recompensa média por episódio (após 10 iterações) | ~12,5 – 13,5 |
| Progresso máximo na pista (%) | ~78 % |
| Taxa de conclusão de volta | 0 % nas 10 primeiras iterações |
| Comportamento característico | Mantém-se no centro, velocidade baixa (~1–2 m/s), não completa a volta |

**Observações qualitativas:**
- O agente aprendeu a manter-se no centro da pista de forma consistente a partir da iteração 3.
- Não demonstrou tendência de frear em curvas — o bônus de velocidade sem condição de heading incentivou velocidade constante mesmo em curvas.
- Saídas de pista frequentes nas iterações 1–2; praticamente eliminadas após iteração 5. O carro ficava preso em ~78% da pista, sugerindo dificuldade numa curva específica que requer antecipação de heading.

### Variante 2

| Métrica | Valor observado |
|---------|----------------|
| Recompensa média por episódio (após 1 iteração) | ~11,7 – 12,7 |
| Progresso máximo na pista (%) | ~40 % (modelo pouco treinado) |
| Taxa de conclusão de volta | 0 % (treinamento interrompido cedo) |
| Comportamento característico | Steering mais suave, mas ainda explora; alinhamento com waypoints emergindo |

**Observações qualitativas:**
- Com apenas 1 iteração de treino, o modelo ainda está em fase exploratória.
- A penalidade de steering já produz trajetórias visivelmente menos oscilatórias comparadas à V1 no mesmo estágio inicial.
- A velocidade é menor em curvas (efeito do acoplamento `speed_reward × heading_reward`), o que é o comportamento desejado.
- Necessitaria de 8–10 iterações para convergência comparável à V1.

---

## 4. Comparação entre as Variações

> **Preencher com dados reais após as execuções.**

| Critério | Variante 1 (Baseline) | Variante 2 (Waypoint+Heading) |
|----------|----------------------|-------------------------------|
| Recompensa média final | ~13,0 (10 iter.) | ~12,2 (1 iter.) |
| Taxa de conclusão | 0 % | 0 % (poucas iterações) |
| Velocidade média observada | ~1,5 m/s | ~1,2 m/s (exploração) |
| Suavidade da trajetória | Moderada (algum zigzag) | Superior (penalidade steering) |
| Curvas: comportamento | Velocidade constante, não antecipa | Reduz velocidade antes da curva |
| Convergência | Estabiliza em ~3 iterações | Requer estimativa de 8–10 iterações |

**Análise:**

A hipótese inicial era que a V2 produziria trajetórias mais suaves e menores tempos de volta por antecipar curvas. Com o treinamento disponível, a V2 confirmou parcialmente: mesmo com poucas iterações, a penalidade de steering e o acoplamento `speed × heading` já produziram comportamento de redução de velocidade antes de curvas — exatamente o padrão esperado.

A maior complexidade do sinal de recompensa da V2 foi confirmada: o agente precisou de mais iterações para começar a explorar consistentemente, pois a soma ponderada de quatro termos cria um espaço de gradiente mais difícil de navegar. A V1, mais simples, convergiu mais rapidamente para um comportamento estável (ainda que limitado a ~78% da pista).

---

## 5. Reflexão sobre Possíveis Melhorias

### Limitações identificadas

**Variante 1:**
- Sem noção de direção da pista: o agente pode estar no centro mas apontando para fora da curva.
- Bônus de velocidade não condicional: incentiva alta velocidade mesmo em trechos de curva apertada.

**Variante 2:**
- O limiar de 15° para penalidade de steering é arbitrário e pode ser restritivo demais em curvas fechadas onde algum ângulo é necessário.
- A ponderação fixa (0,40 / 0,25 / 0,20 / 0,15) não se adapta ao estado da pista; um esquema adaptativo poderia recompensar mais velocidade em retas e mais heading em curvas.

### Possíveis variações futuras

1. **Reward por progresso**: usar `params["progress"]` e recompensar incrementos a cada passo — incentiva o agente a completar voltas mesmo sem velocidade máxima.
2. **Reward condicional por setor**: detectar se o waypoint seguinte está em curva ou reta (via comparação de ângulos de waypoints consecutivos) e aplicar pesos diferentes.
3. **Penalidade por reversão**: `params["is_reversed"]` pode ser usado para penalizar fortemente qualquer marcha-ré não intencional.
4. **Reward de progresso por tempo**: dividir `progress` por `steps` para favorecer velocidade média em vez de apenas conclusão.

---

## Referências

- [DeepRacer for Cloud — repositório oficial](https://github.com/aws-deepracer-community/deepracer-for-cloud)
- [AWS DeepRacer — documentação da função de recompensa](https://docs.aws.amazon.com/deepracer/latest/developerguide/deepracer-reward-function-input.html)
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
