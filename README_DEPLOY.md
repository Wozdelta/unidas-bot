# 🚀 Deploy no Railway - Guia Completo

## 📁 Arquivos Preparados
Todos os arquivos necessários já estão prontos:
- ✅ `Procfile` - Comando para rodar o bot
- ✅ `railway.json` - Configurações do Railway
- ✅ `nixpacks.toml` - Ambiente Linux com Chrome
- ✅ `.gitignore` - Arquivos a ignorar
- ✅ `requirements.txt` - Dependências Python

## 🔗 Passo a Passo

### 1. Criar Repositório no GitHub
1. Acesse [github.com](https://github.com)
2. Clique **"New repository"**
3. Nome: `unidas-bot`
4. Marque **"Public"**
5. Clique **"Create repository"**

### 2. Upload dos Arquivos
**Opção A - Upload Web:**
1. Na página do repositório, clique **"uploading an existing file"**
2. Arraste TODOS os arquivos da pasta `d:\a` (exceto `.env`)
3. Commit message: `Bot monitoramento Unidas`
4. Clique **"Commit changes"**

**Opção B - GitHub Desktop:**
1. Baixe [GitHub Desktop](https://desktop.github.com)
2. Clone o repositório
3. Copie os arquivos
4. Commit e push

### 3. Deploy no Railway
1. Acesse [railway.app](https://railway.app)
2. **"Start a New Project"** → **"Deploy from GitHub repo"**
3. Conecte sua conta GitHub
4. Selecione `unidas-bot`
5. **"Deploy Now"**

### 4. Configurar Variáveis
No Railway dashboard:
- **Variables** → **"New Variable"**
- `WHATSAPP_PHONE_NUMBER` = `+5516997700430`
- `NOTIFICATION_COOLDOWN` = `3600`

### 5. Monitorar
- **Deployments** - Ver logs em tempo real
- **Metrics** - Uso de CPU/RAM
- Bot roda automaticamente 24h!

## 🎯 Resultado Final
- ✅ Bot monitora Unidas a cada 30 minutos
- ✅ Envia WhatsApp quando acha carros
- ✅ Reinicia automaticamente se der erro
- ✅ Logs completos no dashboard

## 🆓 Créditos Gratuitos
- Railway: $5 grátis (dura ~1 mês)
- Depois migre para Oracle Cloud (gratuito para sempre)
