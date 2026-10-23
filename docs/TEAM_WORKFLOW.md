# Fluxo de Trabalho da Equipe — Três Integrantes com IBM Bob

## Visão Geral

| Integrante | IBM Bob | Branch de trabalho            | Responsabilidade principal           |
|------------|---------|-------------------------------|--------------------------------------|
| Bob 1      | Coordenador | `main` + `feature/integracao-testes` | Integração, watsonx, testes, docs |
| Bob 2      | Análise | `feature/analise-antifraude`  | Motor antifraude, dados sintéticos   |
| Bob 3      | Interface | `feature/interface-dashboard` | Interface Streamlit, painel, UX    |

---

## Regras Fundamentais

| ❌ Proibido | ✅ Obrigatório |
|---|---|
| Commitar diretamente na `main` | Sempre via Pull Request revisado |
| `git push --force` | `git push origin feature/sua-branch` |
| Reimplementar lógica de outro módulo | Importar dos contratos definidos |
| Armazenar `.env`, credenciais ou tokens | Usar variáveis de ambiente |
| Fazer merge sem testes passando | Executar `pytest` antes de PR |
| Descartar trabalho de outro integrante | Sempre `git pull` antes de começar |

---

## Configuração Inicial (cada integrante faz uma vez)

### 1. Clonar o repositório

```bash
git clone https://github.com/LeonCS5/sicredi-prevencao-fraudes.git
cd sicredi-prevencao-fraudes
```

### 2. Configurar identidade Git

```bash
git config user.name "Seu Nome"
git config user.email "seu@email.com"
```

### 3. Criar ambiente virtual e instalar dependências

```bash
# Criar ambiente
python -m venv venv

# Ativar — Windows
venv\Scripts\activate

# Ativar — Linux/macOS
source venv/bin/activate

# Instalar dependências
pip install -r sicredi_fraudes/requirements.txt
```

### 4. Ir para a branch do seu módulo

```bash
# Bob 2
git checkout feature/analise-antifraude

# Bob 3
git checkout feature/interface-dashboard

# Bob 1 (coordenador)
git checkout feature/integracao-testes
```

---

## Fluxo de Trabalho Diário

Execute **sempre nesta ordem** ao começar a trabalhar:

```bash
# ── Passo 1: Sincronize a main ──────────────────────────────────────
git fetch origin
git checkout main
git pull origin main

# ── Passo 2: Atualize sua branch com a main ─────────────────────────
git checkout feature/sua-branch
git merge main
# Se houver conflitos: resolva, git add . , git commit

# ── Passo 3: Implemente sua funcionalidade ──────────────────────────
# (edite os arquivos, execute a aplicação para testar)
streamlit run sicredi_fraudes/app.py

# ── Passo 4: Execute os testes ──────────────────────────────────────
pytest sicredi_fraudes/tests/ -v

# ── Passo 5: Revise o que vai enviar ────────────────────────────────
git diff
git status

# ── Passo 6: Adicione e faça commit descritivo ──────────────────────
git add .
git commit -m "feat(modulo): descrição clara do que foi feito"

# ── Passo 7: Envie para o GitHub ─────────────────────────────────────
git push origin feature/sua-branch

# ── Passo 8: Abra um Pull Request ────────────────────────────────────
# Acesse: https://github.com/LeonCS5/sicredi-prevencao-fraudes/compare
# base: main  ←  compare: feature/sua-branch
# Preencha: título descritivo + o que foi feito + como testar

# ── Passo 9: Aguarde revisão ─────────────────────────────────────────
# Outro integrante deve revisar antes do merge
```

---

## Convenção de Commits

Use o padrão **Conventional Commits**:

```
tipo(escopo): descrição curta no presente

[corpo opcional]
```

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `test` | Testes |
| `refactor` | Refatoração sem mudança de comportamento |
| `style` | Formatação, sem mudança de lógica |

**Exemplos:**
```
feat(risk): adiciona regra de detecção de viagem impossível
fix(interface): corrige exibição de pontuação no gauge
docs(watsonx): documenta fluxo agêntico planejado
test(risk): adiciona cenário de desvio padrão zero
```

---

## Pull Requests — Checklist

Antes de abrir um PR, confirme **todos** os itens:

- [ ] `pytest sicredi_fraudes/tests/ -v` — todos os testes passam
- [ ] `git diff --cached` — nenhum `.env`, credencial ou dado real
- [ ] Branch atualizada com a `main` (`git merge main`)
- [ ] Código respeita os contratos em `docs/INTEGRATION_CONTRACTS.md`
- [ ] `streamlit run sicredi_fraudes/app.py` — aplicação inicia sem erros
- [ ] Título do PR descreve claramente a mudança
- [ ] Descrição explica o que foi feito e como testar

---

## Checklist de Revisão (para quem revisa)

- [ ] Os testes existentes continuam passando?
- [ ] O código está dentro da branch correta?
- [ ] Algum contrato de integração foi quebrado?
- [ ] Há algum dado real, credencial ou token?
- [ ] A lógica de risco foi duplicada na interface?
- [ ] A aplicação inicia e o fluxo principal funciona?

---

## Resolução de Conflitos

```bash
# Ver quais arquivos têm conflito
git status

# Para cada arquivo com conflito:
# 1. Abra o arquivo — procure por <<<<<<< HEAD
# 2. Decida qual versão manter (ou combine as duas)
# 3. Remova os marcadores <<<<<<< ======= >>>>>>>
# 4. Salve o arquivo

# Marcar como resolvido e continuar
git add arquivo_resolvido.py
git commit -m "fix: resolve conflito em arquivo_resolvido.py"
```

**Regra de ouro para conflitos:** se tiver dúvida sobre qual versão manter,
comunique a equipe antes de concluir o merge.

---

## Comandos de Referência Rápida

```bash
# Ver status geral
git status

# Ver histórico resumido
git log --oneline --graph --all

# Comparar com a main
git diff main

# Desfazer última alteração não commitada de um arquivo
git checkout -- arquivo.py

# Ver branches remotas
git branch -r

# Atualizar referências remotas sem merge
git fetch origin
```
