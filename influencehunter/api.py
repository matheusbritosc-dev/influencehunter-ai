"""
InfluenceHunter AI - Backend API

API RESTful desenvolvida com FastAPI para servir o frontend da aplicação.
Exerça as funções de:
- Listar influenciadores rankeados
- Disparar coleta de dados
- Servir métricas para o dashboard
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Adiciona diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import connect_db
from database.models import get_all_influencers, save_influencer, update_scores
from ranking.rank_engine import RankEngine
from analyzer.conversion import ConversionAnalyzer
from analyzer.engagement import calculate_engagement
from collector.instagram import InstagramCollector
from collector.tiktok import TikTokCollector

app = FastAPI(
    title="InfluenceHunter AI API",
    description="API para Radar de Afiliados Locais",
    version="1.0.0"
)

# Configurar CORS (Permitir acesso do frontend React)
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Vite default
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para validação e documentação
class InfluencerResponse(BaseModel):
    id: int
    username: str
    platform: str
    niche: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    link_in_bio: Optional[str] = None
    has_whatsapp: bool
    followers: int
    engagement_rate: float
    conversion_potential: float
    sales_language_score: float
    influence_score: float
    calculated_ranking_score: Optional[float] = None

class CollectionRequest(BaseModel):
    platforms: List[str] = ["instagram", "tiktok"]
    limit: int = 15

@app.get("/")
def read_root():
    """Health check"""
    return {"status": "online", "system": "InfluenceHunter AI - Affiliate Radar"}

@app.get("/influencers", response_model=List[InfluencerResponse])
def get_influencers():
    """Retorna lista rankeada de influenciadores (Top Afiliados)"""
    try:
        raw_influencers = get_all_influencers()
        
        # Como get_all_influencers retorna sqlite3.Row, convertemos para dict
        # e aplicamos o ranking engine para garantir a ordem correta
        influencers_list = [dict(row) for row in raw_influencers]
        
        rank_engine = RankEngine()
        ranked_list = rank_engine.rank_influencers_for_affiliate(
            influencers_list, 
            min_conversion_score=0.0
        )
        
        return ranked_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect")
def trigger_collection(request: CollectionRequest):
    """Dispara o processo de coleta (Real ou Simulado)"""
    try:
        # Token do Usuário (Carregado do .env)
        APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
        
        # Inicializa coletores
        # Se 
        use_real_insta = "instagram" in request.platforms
        use_real_tiktok = "tiktok" in request.platforms

        insta_collector = InstagramCollector(
            api_key=APIFY_TOKEN if use_real_insta else None,
            simulated=not use_real_insta
        )
        tiktok_collector = TikTokCollector(
            api_key=APIFY_TOKEN if use_real_tiktok else None, 
            simulated=not use_real_tiktok
        )
        
        profiles = []
        
        # Coleta Instagram (Discovery Mode via Hashtags)
        if "instagram" in request.platforms:
            print(f"Iniciando descoberta Instagram (Real: {use_real_insta})...")
            # Hashtags de infoprodutos/viral
            hashtags = ["marketingdigital", "afiliados", "rendaextra", "hotmart", "kiwify"]
            discovered = insta_collector.discover_from_hashtags(hashtags)
            profiles.extend(discovered)
                
        # Coleta TikTok (Discovery Mode via Dataset)
        if "tiktok" in request.platforms:
            print(f"Iniciando descoberta TikTok (Real: {use_real_tiktok})...")
            discovered = tiktok_collector.discover_from_dataset()
            profiles.extend(discovered)

        
        # Processamento (Análise e Persistência)
        conversion_analyzer = ConversionAnalyzer()
        rank_engine = RankEngine()
        
        saved_count = 0
        
        for profile in profiles:
            # 1. Engajamento
            engagement_rate = calculate_engagement(
                profile['avg_likes'], 
                profile['avg_comments'], 
                profile['followers']
            )
            
            # 2. Conversão
            conversion, sales_score, has_wpp = conversion_analyzer.calculate_conversion_potential(
                bio=profile['bio'],
                has_link=bool(profile['link_in_bio']),
                posts_captions=profile['captions'],
                comments_text=profile['comments_text']
            )
            
            # 3. Métricas extras (simuladas)
            authenticity = profile.get('authenticity_score', 85.0)
            growth = profile.get('growth_rate', 5.0)
            
            # 4. Salvar
            data_to_save = {
                "username": profile['username'],
                "platform": profile['platform'],
                "niche": profile['niche'],
                "city": profile['city'],
                "bio": profile['bio'],
                "link_in_bio": profile['link_in_bio'],
                "has_link_in_bio": bool(profile['link_in_bio']),
                "has_whatsapp": has_wpp,
                "sales_language_score": sales_score,
                "followers": profile['followers'],
                "avg_likes": profile['avg_likes'],
                "avg_comments": profile['avg_comments'],
            }
            
            if save_influencer(data_to_save):
                saved_count += 1
            
            # 5. Calcular Referência e Atualizar
            temp_calc = {
                'conversion_potential': conversion,
                'engagement_rate': min(100.0, engagement_rate * 10),
                'authenticity_score': authenticity,
                'growth_rate': growth
            }
            influence_score = rank_engine.calculate_overall_score(temp_calc)
            
            update_scores(
                username=profile['username'],
                engagement=engagement_rate,
                growth=growth,
                conversion=conversion,
                authenticity=authenticity,
                influence=influence_score,
                sales_score=sales_score
            )
            
        return {
            "status": "success", 
            "message": f"Coleta finalizada. {saved_count} perfis processados.",
            "details": f"Plataformas: {request.platforms}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Executa a API na porta 8000
    uvicorn.run(app, host="127.0.0.1", port=8001)
