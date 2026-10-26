# Contratos de Integração — Interfaces Compartilhadas

Este documento define os **contratos técnicos estáveis** entre os módulos.
Nenhum integrante deve alterar as assinaturas abaixo sem comunicação prévia à equipe.

---

## 1. Contrato do Motor Antifraude

**Arquivo:** [`sicredi_fraudes/src/core/risk_engine.py`](../sicredi_fraudes/src/core/risk_engine.py)  
**Responsável:** Bob 2 (branch `feature/analise-antifraude`)

### Função principal

```python
def avaliar_transacao(
    tx: Transacao,
    perfil: PerfilAssociado,
    historico_recente: List[Transacao] | None = None,
) -> ResultadoAnalise:
```

| Parâmetro           | Tipo                   | Descrição                                      |
|---------------------|------------------------|------------------------------------------------|
| `tx`                | `Transacao`            | A transação a ser analisada                    |
| `perfil`            | `PerfilAssociado`      | Perfil histórico fictício do associado         |
| `historico_recente` | `List[Transacao] | None` | Transações recentes do mesmo associado (pode ser vazio) |

**Retorno:** `ResultadoAnalise`

**Invariantes garantidas:**
- `0.0 ≤ pontuacao ≤ 100.0`
- `nivel_risco ∈ {"baixo", "medio", "alto"}`
- `eh_fraude_confirmada == False` sempre (nunca confirmada automaticamente)
- `fonte_analise == "motor_local"` (salvo enriquecimento watsonx)
- Nunca lança exceção para entradas válidas

---

## 2. Modelos de Dados

**Arquivo:** [`sicredi_fraudes/src/core/models.py`](../sicredi_fraudes/src/core/models.py)

### `Transacao`

```python
@dataclass
class Transacao:
    id: str                           # identificador único da transação
    associado_id: str                 # identificador do associado
    valor: float                      # valor em R$
    data_hora: datetime               # data e hora da transação
    categoria: str                    # ex.: "Supermercado", "Eletrônicos"
    estabelecimento: str              # nome do estabelecimento
    cidade: str                       # cidade da transação
    estado: str                       # sigla do estado (ex.: "RS")
    pais: str = "Brasil"              # país da transação
    distancia_residencia_km: float = 0.0   # distância estimada da residência
    canal: str = "Presencial"         # "Presencial" | "Online" | "App"
```

### `PerfilAssociado`

```python
@dataclass
class PerfilAssociado:
    associado_id: str
    nome: str                              # nome fictício
    valor_medio_transacao: float           # média histórica de valor (R$)
    desvio_padrao_valor: float             # variação habitual (R$)
    categorias_frequentes: list            # ex.: ["Supermercado", "Farmácia"]
    cidades_frequentes: list               # cidades habituais de compra
    limite_diario: float                   # limite diário do cartão (R$)
    transacoes_por_hora_normal: float      # taxa normal de uso
    horario_habitual_inicio: int           # hora início do padrão (0-23)
    horario_habitual_fim: int              # hora fim do padrão (0-23)
```

### `FatorRisco`

```python
@dataclass
class FatorRisco:
    nome: str          # ex.: "Valor elevado", "Localização incomum"
    descricao: str     # texto explicativo para exibição ao usuário
    pontos: float      # contribuição para pontuação total (0-25 por fator)
    nivel: str         # "baixo" | "medio" | "alto"
```

### `ResultadoAnalise`

```python
@dataclass
class ResultadoAnalise:
    transacao_id: str               # mesmo id de Transacao.id
    associado_id: str               # mesmo id de Transacao.associado_id
    pontuacao: float                # 0.0 – 100.0
    nivel_risco: str                # "baixo" | "medio" | "alto"
    fatores: list                   # List[FatorRisco] — pode ser vazia
    recomendacao: str               # ação recomendada (para exibição)
    justificativa: str              # explicação dos fatores
    eh_fraude_confirmada: bool      # sempre False — apenas indicação
    analisado_em: datetime          # timestamp da análise
    fonte_analise: str              # "motor_local" | "watsonx"
```

---

## 3. Contrato do Gerador de Dados

**Arquivo:** [`sicredi_fraudes/src/data/generator.py`](../sicredi_fraudes/src/data/generator.py)  
**Responsável:** Bob 2

### Funções exportadas

```python
# Dataset completo de demonstração
def gerar_dataset_demo(
    n_normais: int = 40,
    n_suspeitas: int = 10,
) -> Tuple[List[PerfilAssociado], List[Transacao]]:
    ...

# Perfil individual
def gerar_perfil(
    associado_id: str | None = None,
    rng: random.Random | None = None,
) -> PerfilAssociado:
    ...

# Constantes disponíveis para a interface
CATEGORIAS: List[str]       # lista de categorias disponíveis
CIDADES_BRASIL: List[str]   # lista de cidades disponíveis
```

---

## 4. Contrato do Cliente watsonx

**Arquivo:** [`sicredi_fraudes/src/core/watsonx_client.py`](../sicredi_fraudes/src/core/watsonx_client.py)

```python
# Verifica status da integração (safe — nunca lança exceção)
def status_integracao() -> dict:
    # Retorna:
    # {
    #   "habilitado": bool,
    #   "mensagem": str
    # }

# Enriquece explicação via LLM (retorna None se indisponível)
def enriquecer_explicacao(
    pontuacao: float,
    nivel_risco: str,
    fatores_resumo: str,
    dados_transacao: str,
) -> str | None:
    ...
```

**Garantia:** ambas as funções são seguras para chamar mesmo sem credenciais configuradas.

---

## 5. Regras de Compatibilidade

| Regra | Descrição |
|---|---|
| **Não duplicar lógica** | A interface (Bob 3) nunca reimplementa cálculo de risco |
| **Campos estáveis** | Campos de `models.py` não são alterados sem consenso |
| **Importação por módulo** | Sempre importar de `src.core.*` — nunca copiar código |
| **Nenhum dado real** | Gerador nunca usa dados reais; interface nunca exibe CPF/CNPJ reais |
| **Falha silenciosa watsonx** | Código que usa watsonx deve tratar `None` como retorno válido |

---

## 6. Exemplo de Uso Completo (referência para Bob 3)

```python
from src.core.models import Transacao
from src.core.risk_engine import avaliar_transacao
from src.data.generator import gerar_perfil, CATEGORIAS
from datetime import datetime

# Criar transação fictícia
tx = Transacao(
    id="TX_EXEMPLO",
    associado_id="ASS001",
    valor=1500.0,
    data_hora=datetime(2025, 6, 15, 3, 22, 0),
    categoria="Joalheria",
    estabelecimento="Joalheria Exemplo",
    cidade="São Paulo",
    estado="SP",
    pais="Brasil",
    distancia_residencia_km=1100.0,
    canal="Online",
)

# Criar/carregar perfil
perfil = gerar_perfil("ASS001")

# Analisar (historico pode ser lista vazia ou None)
resultado = avaliar_transacao(tx, perfil, historico_recente=[])

# Usar resultado na interface
print(f"Pontuação: {resultado.pontuacao}/100")
print(f"Nível: {resultado.nivel_risco}")
print(f"Recomendação: {resultado.recomendacao}")
for fator in resultado.fatores:
    print(f"  - {fator.nome}: {fator.descricao}")
```
