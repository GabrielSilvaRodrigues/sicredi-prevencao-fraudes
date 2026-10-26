# Prompt para Bob 2 — Motor de Análise Antifraude

> **INSTRUÇÃO PARA O INTEGRANTE 2 (IBM Bob no segundo computador)**
>
> Cole este prompt inteiro no IBM Bob para receber instruções precisas sobre sua tarefa.
> Leia completamente antes de executar qualquer comando.

---

## Contexto do Projeto

Você está contribuindo para um projeto de competição do Sicredi chamado
**"Prevenção Inteligente a Fraudes e Segurança do Associado"**.

O projeto é um protótipo de agente de IA que analisa transações fictícias de cartão
e identifica sinais suspeitos usando um motor de avaliação de risco.

**Repositório:** `https://github.com/LeonCS5/sicredi-prevencao-fraudes`  
**Sua branch:** `feature/analise-antifraude`  
**Sua responsabilidade:** Motor antifraude, regras de risco, gerador de dados, testes

---

## Primeiro Passo: Configurar o Ambiente

```bash
# 1. Clone o repositório (se ainda não clonou)
git clone https://github.com/LeonCS5/sicredi-prevencao-fraudes.git
cd sicredi-prevencao-fraudes

# 2. Configure seu nome e e-mail Git
git config user.name "Seu Nome"
git config user.email "seu@email.com"

# 3. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

# 4. Instale as dependências
pip install -r sicredi_fraudes/requirements.txt

# 5. Vá para sua branch
git checkout feature/analise-antifraude

# 6. Verifique o que já existe
git log --oneline
```

---

## O que já está implementado (na main)

Antes de escrever código, examine o que já existe:

| Arquivo | O que contém |
|---|---|
| `sicredi_fraudes/src/core/models.py` | Modelos: `Transacao`, `PerfilAssociado`, `FatorRisco`, `ResultadoAnalise` |
| `sicredi_fraudes/src/core/risk_engine.py` | Motor: `avaliar_transacao()` + 7 regras |
| `sicredi_fraudes/src/data/generator.py` | Gerador de dados sintéticos |
| `sicredi_fraudes/tests/test_risk_engine.py` | Testes: 6 cenários + regras individuais |
| `sicredi_fraudes/tests/conftest.py` | Fixtures: `tx_normal`, `perfil_padrao`, `dataset_demo` |

**Execute os testes para confirmar que o código base funciona:**

```bash
pytest sicredi_fraudes/tests/ -v
```

---

## O que você deve fazer

### Tarefa 1 — Executar e validar os testes existentes

```bash
pytest sicredi_fraudes/tests/ -v --tb=short
```

Todos os testes devem passar. Se algum falhar, analise o motivo antes de continuar.

### Tarefa 2 — Revisar as regras existentes e calibrar os pesos

Abra `sicredi_fraudes/src/core/risk_engine.py` e verifique:

1. Os pesos `PESO_*` no topo do arquivo
2. Execute o dataset demo e veja a distribuição de risco:

```python
# Execute este script para ver a distribuição atual
import sys; sys.path.insert(0, 'sicredi_fraudes')
from src.data.generator import gerar_dataset_demo
from src.core.risk_engine import avaliar_transacao

perfis, txs = gerar_dataset_demo(40, 10)
perfis_d = {p.associado_id: p for p in perfis}
resultados = [avaliar_transacao(tx, perfis_d[tx.associado_id]) for tx in txs]
niveis = [r.nivel_risco for r in resultados]
print({n: niveis.count(n) for n in ['baixo','medio','alto']})
```

Ajuste os pesos se a distribuição estiver muito desbalanceada.

### Tarefa 3 — Implementar nova regra: Viagem Impossível (opcional, alta prioridade)

Adicione em `risk_engine.py` a regra `regra_viagem_impossivel()`:

**Conceito:** se o mesmo associado fez duas transações em cidades distantes em menos de 1 hora,
é fisicamente impossível sem teleporte — sinal forte de uso simultâneo do cartão.

```python
def regra_viagem_impossivel(
    tx: Transacao,
    historico_recente: List[Transacao],
    velocidade_maxima_kmh: float = 800.0,  # avião comercial
) -> FatorRisco | None:
    """
    Detecta transações geograficamente impossíveis em curto intervalo.
    Usa distancia_residencia_km como proxy (não temos coordenadas exatas).
    """
    # Implemente aqui
    ...
```

**Importante:** adicione o peso `PESO_VIAGEM_IMPOSSIVEL = 30` e inclua a regra
no loop de `avaliar_transacao()`.

**Adicione testes** em `test_risk_engine.py` para esta regra.

### Tarefa 4 — Expandir cobertura de testes

Adicione testes para cenários não cobertos:

```python
# Sugestões de casos a testar:
# - gerar_transacao_suspeita() para cada tipo_suspeita
# - transacoes_para_dataframe() com lista vazia
# - gerar_dataset_demo() — verificar que retorna > 0 transações
# - Regra de canal suspeito com valor < 500 (deve retornar None)
# - Regra de país estrangeiro com "Brazil" em inglês (deve retornar None)
```

---

## Contratos que você DEVE respeitar

### Assinatura obrigatória da função principal

```python
# NÃO altere esta assinatura
def avaliar_transacao(
    tx: Transacao,
    perfil: PerfilAssociado,
    historico_recente: List[Transacao] | None = None,
) -> ResultadoAnalise:
```

### Campos obrigatórios no ResultadoAnalise

```python
resultado.transacao_id          # str — igual a tx.id
resultado.associado_id          # str — igual a tx.associado_id
resultado.pontuacao             # float 0.0-100.0
resultado.nivel_risco           # "baixo" | "medio" | "alto"
resultado.fatores               # List[FatorRisco]
resultado.recomendacao          # str não vazio
resultado.justificativa         # str não vazio
resultado.eh_fraude_confirmada  # SEMPRE False
resultado.fonte_analise         # "motor_local"
```

### Regras de ouro

- ❌ NÃO altere os campos de `models.py` sem comunicar a equipe
- ❌ NÃO importe Streamlit nem pandas no motor de risco
- ❌ NÃO faça chamadas à internet no motor de risco
- ✅ Cada regra deve ser uma função pura e testável independentemente
- ✅ `eh_fraude_confirmada` deve ser sempre `False`
- ✅ `pontuacao` deve estar sempre entre 0.0 e 100.0

---

## Como fazer commit e enviar

```bash
# Verificar o que mudou
git diff
git status

# Executar testes antes de commitar
pytest sicredi_fraudes/tests/ -v

# Adicionar e commitar
git add sicredi_fraudes/src/core/risk_engine.py
git add sicredi_fraudes/tests/test_risk_engine.py
git commit -m "feat(risk): adiciona regra de viagem impossivel com testes"

# Enviar para o GitHub
git push origin feature/analise-antifraude
```

Depois, abra um **Pull Request** em:
`https://github.com/LeonCS5/sicredi-prevencao-fraudes/compare`  
(base: `main` ← compare: `feature/analise-antifraude`)

---

## Perguntas frequentes

**P: Posso alterar os modelos em `models.py`?**  
R: Somente se for imprescindível e após comunicar a equipe. A interface (Bob 3) depende
desses campos — qualquer alteração pode quebrar o painel.

**P: Posso usar bibliotecas de ML externas?**  
R: Para este protótipo, mantenha o motor em Python puro. Bibliotecas como
`scikit-learn` podem ser adicionadas na branch `feature/analise-antifraude`
se necessário, mas precisam ser documentadas no `requirements.txt`.

**P: O watsonx vai substituir meu motor?**  
R: Não. O watsonx enriquece apenas a *explicação textual*. Sua pontuação e seus
fatores de risco nunca são alterados pelo watsonx.
