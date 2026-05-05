# ponderada-deepracer

# Link do video:
https://youtu.be/8OYVzKITCa4

# Análise de Funções de Recompensa — DeepRacer for Cloud

**Aluno:** Lucas Ramenzoni Jorge
**Instituição:** Inteli - Instituto de Tecnologia e Liderança  
**Data:** Maio de 2026  

---

## 🔗 Link para o Vídeo da Simulação
**[[Link]](https://youtu.be/8OYVzKITCa4)**

---

## 1. Descrição das Funções de Recompensa

Para este experimento, foram propostas e implementadas duas funções de recompensa distintas para avaliar o comportamento do agente de Reinforcement Learning:

### Variante 1 — Baseline: Centro da Pista + Velocidade (`variant_1_baseline.py`)
Uma abordagem reativa e geométrica. A pista é dividida em três faixas concêntricas, atribuindo recompensas decrescentes conforme o veículo se afasta da linha central (1.0 para 10% da largura, 0.5 para 25% e 0.1 para 50%). A isso, soma-se um bônus linear de velocidade normalizado entre 1.0 m/s e 4.0 m/s.
* **Composição:** `0.7 * center_reward + 0.3 * speed_reward`
* **Punição:** Sair da pista ou não ter todas as rodas no traçado retorna a recompensa mínima (0.001) imediatamente.

### Variante 2 — Avançada: Waypoint Heading + Direção Suave (`variant_2_waypoint_heading.py`)
Uma abordagem preditiva. Em vez de apenas se manter no centro, o agente é recompensado por alinhar a frente do carro (heading) com o próximo *waypoint* da pista, utilizando uma função de decaimento suave (cosseno do erro de ângulo). Além disso, há uma penalidade para ângulos de direção maiores que 15°, visando evitar oscilações bruscas (zigzag).
* **Composição:** `0.40 * heading_reward + 0.25 * (speed_reward * heading_reward) + 0.20 * center_reward + 0.15 * steering_penalty`
* **Acoplamento:** O bônus de velocidade só é concedido integralmente se o agente estiver bem alinhado com o *waypoint*, desencorajando a aceleração em trajetórias incorretas.

---

## 2. Justificativa das Escolhas

A **Variante 1 (Baseline)** foi escolhida para servir como variável de controle experimental. Por ser simples e intuitiva, ela nos permite entender o comportamento basal do agente quando incentivado puramente a "ficar na pista e acelerar". 

A **Variante 2 (Waypoint Heading)** foi desenhada para resolver as limitações teóricas da Variante 1. Um carro guiado apenas pelo centro tende a reagir muito tarde nas curvas. A introdução do *heading* força o agente a "olhar para a frente" e antecipar o traçado. A penalidade de direção (*steering*) foi implementada para combater um problema clássico no DeepRacer: a tendência do agente de ziguezaguear pelo centro para maximizar a recompensa posicional, desperdiçando energia cinética.

---

## 3. Análise do Comportamento Observado

As simulações foram executadas localmente. Devido às severas restrições de processamento de um hardware de uso geral (notebook sem aceleração dedicada de GPU para o ambiente DeepRacer), o comportamento observado em ambas as simulações foi atípico, porém altamente instrutivo sobre a mecânica de aprendizado de máquina.

Ao analisar o vídeo das execuções, nota-se que:
* **Falta de Convergência:** O agente permaneceu estritamente na fase de exploração aleatória inicial. O contador do simulador registrou mais de 100 *resets* em um intervalo de aproximadamente 2 minutos.
* **Ciclo de Falha Rápida:** O carro "nasce" (spawn), executa uma ação de direção brusca aleatória impulsionada por pesos neurais ainda não calibrados, falha quase instantaneamente e é resetado.
* O agente não conseguiu acumular *episodes* (episódios) consistentes o suficiente para criar a correlação entre as ações de direção/aceleração e as recompensas mapeadas no código. 

---

## 4. Comparação entre as Variações de Reward

A expectativa teórica era de que a Variante 2 apresentasse um tempo de volta inferior e um traçado mais limpo. Contudo, a restrição de infraestrutura revelou um ponto crítico em Reinforcement Learning: **a dependência da capacidade de exploração e acúmulo de estado.**

* **Desempenho Estático:** Ambas as funções resultaram no mesmo padrão de *reset* contínuo. Nenhuma das duas apresentou vantagem competitiva no tempo de execução disponível.
* **Complexidade vs. Tempo de Treino:** A Variante 2 introduz uma função de perda (*loss*) muito mais complexa para o otimizador resolver (relacionando ângulo, velocidade condicional e centro). Na prática, modelos com funções de recompensa tão fragmentadas exigem ciclos de exploração (treinamento) significativamente maiores para convergir em comparação a lógicas simples como a da Variante 1. A ausência de hardware mitigou qualquer benefício do design algorítmico sofisticado.

---

## 5. Reflexão sobre Possíveis Melhorias

A principal lição deste experimento não reside no código, mas na pipeline de execução. Para aprimorar os resultados e realmente validar as funções matemáticas criadas, as seguintes melhorias são mandatórias:

1. **Infraestrutura de Treinamento:** Migrar a execução local para instâncias AWS especializadas em Deep Learning ou utilizar o servidor institucional dedicado, fornecendo os recursos computacionais (vGPUs e memória) necessários para que o agente saia da fase de exploração cega e inicie a fase de exploração guiada pela política de recompensa.
2. **Tempo de Simulação:** Ampliar o tempo de treinamento. Funções de recompensa contendo múltiplas variáveis (como a Variante 2) frequentemente precisam de horas de processamento assíncrono para estabelecer uma convergência estável da rede neural.
3. **Refinamento Algorítmico Progressivo:** Iniciar o treinamento do agente com uma função de recompensa focada apenas em `progress` (progresso na pista), para incentivar o movimento para frente contínuo e, em ciclos de treinamento posteriores (clonagem do modelo), inserir lógicas de precisão como `heading` e suavização de `steering`.
