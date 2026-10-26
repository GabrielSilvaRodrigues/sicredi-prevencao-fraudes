# 🤝 Guia de Colaboração — Equipe Sicredi

Este guia descreve como os três integrantes devem trabalhar juntos neste repositório.

---

## 🏗️ Estrutura de Branches

| Branch                       | Integrante                  | Responsabilidade                              |
|------------------------------|-----------------------------|-----------------------------------------------|
| `main`                       | Todos (somente via PR)      | Branch principal — código revisado e testado  |
| `feature/analise-fraudes`    | Integrante 1                | Motor de risco, regras, modelos de dados      |
| `feature/interface`          | Integrante 2                | Interface Streamlit, gráficos, UX             |
| `feature/integracao-testes`  | Integrante 3                | watsonx, testes automatizados, documentação   |

> ❌ **Ninguém faz commit direto na `main`.**  
> ✅ **Toda alteração entra via Pull Request com revisão.**

---

## 🚀 Como os outros dois integrantes acessam o projeto

### 1. Ser adicionado como colaborador

O dono do repositório (`LeonCS5`) deve acessar:

```
https://github.com/LeonCS5/sicredi-prevencao-fraudes/settings/access
```

→ Clique em **"Add people"** → informe o usuário GitHub de cada integrante → escolha a permissão **"Write"**.

### 2. Aceitar o convite

Cada integrante receberá um e-mail do GitHub ou verá a notificação em:
```
https://github.com/notifications
```

### 3. Clonar o repositório (cada integrante faz isso uma única vez)

```bash
git clone https://github.com/LeonCS5/sicredi-prevencao-fraudes.git
cd sicredi-prevencao-fraudes
```

### 4. Criar o ambiente virtual e instalar dependências

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r sicredi_fraudes/requirements.txt
```

### 5. Ir para a branch correspondente

```bash
# Integrante 1 — análise de fraudes
git checkout feature/analise-fraudes

# Integrante 2 — interface
git checkout feature/interface

# Integrante 3 — integração e testes
git checkout feature/integracao-testes
```

---

## 🔄 Fluxo de Trabalho Diário

Execute estes passos **sempre** ao começar a trabalhar:

```bash
# 1. Atualize a referência da main
git fetch origin
git checkout main
git pull origin main

# 2. Atualize sua própria branch com o que há na main
git checkout feature/sua-branch
git merge main
# Se houver conflitos, resolva-os antes de continuar

# 3. Implemente sua funcionalidade
# (edite, crie, mova arquivos conforme necessário)

# 4. Execute os testes
pytest sicredi_fraudes/tests/ -v

# 5. Revise o que vai enviar
git diff
git status

# 6. Adicione os arquivos alterados
git add .
# ou somente arquivos específicos:
git add sicredi_fraudes/src/core/risk_engine.py

# 7. Crie um commit descritivo
git commit -m "feat(analise): adiciona regra de deteccao de viagem rapida"
# Formatos sugeridos para o prefixo:
# feat(modulo): nova funcionalidade
# fix(modulo): corrige bug
# docs(modulo): atualiza documentacao
# test(modulo): adiciona ou corrige testes
# refactor(modulo): melhoria sem mudar comportamento

# 8. Envie sua branch para o GitHub
git push origin feature/sua-branch

# 9. Abra um Pull Request
# Acesse: https://github.com/LeonCS5/sicredi-prevencao-fraudes/compare
# Selecione: base = main, compare = feature/sua-branch
# Preencha: título, descrição do que foi feito, como testar

# 10. Aguarde revisão
# Outro integrante deve revisar antes do merge
```

---

## ⚠️ Regras de Segurança

| ❌ Nunca fazer | ✅ Sempre fazer |
|---|---|
| `git push --force` | `git push origin feature/sua-branch` |
| Commit direto na `main` | Pull Request com revisão |
| Armazenar `.env` ou chaves no código | Usar `os.getenv()` ou `secrets.toml` (excluído do git) |
| Fazer merge sem testes passando | Rodar `pytest` antes do PR |
| Compartilhar o `.streamlit/secrets.toml` | Cada integrante cria o seu localmente |
| Apagar o trabalho do outro | Sempre `git pull` antes de começar |

---

## 🔑 Configuração de Credenciais (cada integrante, localmente)

Para habilitar a integração com IBM watsonx, crie na pasta raiz:

```
.streamlit/secrets.toml
```

Com o conteúdo (nunca commitar este arquivo):

```toml
WATSONX_API_KEY    = "sua-chave-aqui"
WATSONX_PROJECT_ID = "seu-project-id"
WATSONX_URL        = "https://us-south.ml.cloud.ibm.com"
```

Este arquivo já está no `.gitignore` — ele **nunca irá para o GitHub**.

---

## 📬 Pull Request — Checklist

Antes de abrir um PR, confirme:

- [ ] Os testes passam: `pytest sicredi_fraudes/tests/ -v`
- [ ] Não há arquivos `.env` ou credenciais no commit: `git diff --cached`
- [ ] O título do PR descreve claramente a mudança
- [ ] Há uma breve descrição do que foi feito e como testar
- [ ] A branch está atualizada com a `main` (`git merge main`)

---

## 📞 Comunicação

Em caso de conflito de código ou dúvida sobre a divisão de trabalho,
comunique a equipe **antes** de fazer merge. Prefira resolver conflitos
em conjunto via chamada ou chat.
