# 🎂 Purble Bakery (Comfy Cakes Edition)

Um jogo desenvolvido em Python com **Pygame**, inspirado no clássico e nostálgico minijogo de fazer bolos do **Purble Place** (Windows 7).

O jogo roda em **modo janela (1024x640)** e conta com **4 fases com níveis crescentes de dificuldade**, efeitos sonoros sintetizados nativos, esteira transportadora animada e sistema de pontuação e estrelas.

---

## 🎮 Como Jogar

1. **Observe a TV de Pedidos (Canto Superior Esquerdo):**
   - O cliente mostra uma foto do bolo encomendado e o tempo limite disponível.
2. **Estações de Trabalho na Esteira:**
   - **Estação 1 - Formas (Pans):** Escolha o formato da assadeira (*Quadrado, Redondo, Coração ou Estrela*).
   - **Estação 2 - Massas (Batters):** Despeje a massa do bolo (*Baunilha, Chocolate ou Morango*).
   - **Estação 3 - Recheios (Fillings):** Aplique a camada de recheio cremoso (*Creme de Baunilha, Ganache de Chocolate ou Geleia de Morango*).
   - **Estação 4 - Coberturas (Glazes):** Despeje o glacê decorativo (*Glacê Branco, Chocolate Cremoso ou Rosa Morango*).
   - **Estação 5 - Confeitos (Toppings):** Adicione o toque final (*Cereja, Morango Fresco, Estrela de Açúcar ou Vela com chama animada*).
3. **Bolos de Vários Andares (Fases 3 e 4):**
   - Use o botão **`+ NOVO ANDAR`** para empilhar uma nova camada por cima da massa atual!
4. **Finalização:**
   - Clique em **`⭐ ENTREGAR BOLO`** para enviar para o cliente e pontuar.
   - Se errar algum ingrediente, clique em **`🗑️ DESCARTAR`** para puxar um novo prato limpo.

---

## 🏆 As 4 Fases do Jogo

| Fase | Título | Características e Desafios | Meta |
| :--- | :--- | :--- | :--- |
| **Fase 1** | **Aprendiz de Confeiteiro** | Bolos simples de 1 andar, 2 formatos (*Quadrado, Redondo*), 2 massas, 2 coberturas e 2 confeitos. Sem recheio. Tempo calmo (60s). | 3 bolos |
| **Fase 2** | **Confeiteiro Júnior** | Introdução do formato Coração e da **Estação de Recheios** (3 opções deliciosas). Tempo moderado (50s). | 4 bolos |
| **Fase 3** | **Mestre Confeiteiro** | **Bolos de 2 Andares!** 4 formatos (incluindo Estrela), velas de aniversário e montagem em camadas. | 5 bolos |
| **Fase 4** | **Grande Chefe Purble** | **Bolos complexos de até 3 andares**, velocidade rápida contra o relógio (40s) e multiplicador de combo! | 6 bolos |

---

## 🚀 Como Executar

### Opção 1: Executável Batch (Windows)
Dê um duplo clique no arquivo:
```
F:\isly\run.bat
```

### Opção 2: Pelo Terminal / Prompt de Comando
```bash
cd F:\isly
python main.py
```

---

## 🛠️ Requisitos
- Python 3.8+
- Pygame (`pip install pygame`)
- Totalmente autocontido: os efeitos sonoros e músicas são gerados proceduralmente sem necessidade de downloads externos.
