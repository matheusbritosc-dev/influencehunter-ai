# 🔍 InfluenceHunter AI

> Radar de Afiliados Locais — Encontre influenciadores que vendem, não apenas os que têm fama.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Sobre

O **InfluenceHunter AI** é um sistema inteligente de prospecção de afiliados que vai além das métricas de vaidade. Ele analisa influenciadores do Instagram e TikTok para identificar quem realmente tem **potencial de conversão** para vender infoprodutos.

### 🎯 Diferencial
Em vez de ranquear por número de seguidores, o sistema avalia:
- **Linguagem de vendas** nas legendas e bio
- **Potencial de conversão** (link na bio, WhatsApp, CTAs)
- **Engajamento real** (likes + comentários / seguidores)
- **Autenticidade** do perfil
- **Score de Afiliado** composto e ponderado

## 🏗️ Arquitetura

```
influencehunter/
├── main.py                       # Pipeline principal
├── config.py                     # Configurações
├── api.py                        # API endpoints
├── collector/
│   ├── instagram.py              # Coletor Instagram (simulado)
│   └── tiktok.py                 # Coletor TikTok (simulado)
├── analyzer/
│   ├── engagement.py             # Análise de engajamento
│   ├── conversion.py             # Análise de conversão
│   ├── authenticity.py           # Análise de autenticidade
│   └── growth.py                 # Análise de crescimento
├── classifier/
│   └── niche_classifier.py       # Classificador de nicho
├── database/
│   ├── connection.py             # Conexão SQLite
│   └── models.py                 # Modelos de dados
├── ranking/
│   └── rank_engine.py            # Motor de ranking
├── export/
│   └── export_csv.py             # Exportação CSV
└── frontend/                     # Dashboard React/Vite (TypeScript)
    ├── src/
    │   ├── App.tsx
    │   └── main.tsx
    └── package.json
```

## 🚀 Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USER/influencehunter-ai.git
cd influencehunter-ai

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o pipeline
python -m influencehunter.main
```

### Dashboard (Frontend)
```bash
cd frontend
npm install
npm run dev
```

## 📊 Output

O sistema gera:
- **Ranking no terminal** com Top 10 afiliados
- **Arquivo CSV** com todos os dados exportados em `exports/`
- **Dashboard web** para visualização interativa

## 🧠 Métricas Analisadas

| Métrica | Peso | Descrição |
|---------|------|-----------|
| Conversão | 40% | Linguagem de vendas, CTAs, links |
| Engajamento | 30% | Interação real da audiência |
| Autenticidade | 20% | Perfil genuíno vs. bots |
| Crescimento | 10% | Tendência de crescimento |

## 🛠️ Tech Stack

- **Backend:** Python 3.10+
- **Database:** SQLite
- **Frontend:** React + Vite + TypeScript
- **Análise:** NLP para detecção de linguagem de vendas

## 📄 Licença

MIT License — Desenvolvido por **Matheus Brito**
