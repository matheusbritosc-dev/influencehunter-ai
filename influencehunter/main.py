"""
InfluenceHunter AI - Main Application Entry Point

Este e o ponto de entrada principal da aplicacao InfluenceHunter AI.
MODO: Radar de Afiliados Locais para Infoprodutos.

Ele nao busca fama. Ele busca gente que vende.

Responsavel por:
- Coletar dados (Instagram & TikTok)
- Classificar nicho
- Calcular engajamento
- Calcular autenticidade
- Calcular potencial de conversao
- Calcular Influence Score afiliado
- Gerar ranking
- Exportar CSV
"""

import sys
import os
import random

# Adiciona o diretorio atual ao path para importacoes funcionarem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import create_tables, connect_db
from database.models import save_influencer, get_all_influencers, update_scores
from ranking.rank_engine import RankEngine
from export.export_csv import CSVExporter
from analyzer.conversion import ConversionAnalyzer
from analyzer.engagement import calculate_engagement

# Importando coletores novos
from collector.instagram import InstagramCollector
from collector.tiktok import TikTokCollector

def main():
    """
    Funcao principal que executa o pipeline de Radar de Afiliados
    """
    print("\n[InfluenceHunter AI] - Radar de Afiliados Locais iniciada...\n")
    
    # 1. Setup Database
    conn = connect_db()
    if not conn:
        return
    create_tables(conn)
    conn.close()
    
    # 2. Inicializar Coletores (Simulados)
    # Em producao, passariamos chaves de API reais aqui
    insta_collector = InstagramCollector(api_key=None, simulated=True)
    tiktok_collector = TikTokCollector(api_key=None, simulated=True)
    
    # Lista de alvos para busca (Simulando uma entrada de busca)
    target_usernames_insta = [f"insta_user_{i}" for i in range(1, 9)]
    target_usernames_tiktok = [f"tiktok_star_{i}" for i in range(1, 9)]
    
    print(f"Iniciando coleta em {len(target_usernames_insta)} perfis Instagram e {len(target_usernames_tiktok)} TikTok...")
    
    profiles = []
    
    # Coleta Instagram
    for username in target_usernames_insta:
        data = insta_collector.collect_profile(username)
        profiles.append(data)
        
    # Coleta TikTok
    for username in target_usernames_tiktok:
        data = tiktok_collector.collect_profile(username)
        profiles.append(data)
        
    print(f"\n[OK] {len(profiles)} perfis coletados e normalizados.\n")
    
    # Inicializar Analisadores
    conversion_analyzer = ConversionAnalyzer()
    rank_engine = RankEngine()
    
    print("Processando analises de inteligencia...")
    
    for profile in profiles:
        # Calcular Engajamento
        engagement_rate = calculate_engagement(
            profile['avg_likes'], 
            profile['avg_comments'], 
            profile['followers']
        )
        
        # Calcular Potencial de Conversao (Retorna tupla com metadados)
        conversion_score, sales_score, has_whatsapp = conversion_analyzer.calculate_conversion_potential(
            bio=profile['bio'],
            has_link=bool(profile['link_in_bio']),
            posts_captions=profile['captions'],
            comments_text=profile['comments_text']
        )
        
        # Simular Autenticidade e Crescimento (placeholders por enquanto)
        authenticity_score = random.uniform(70, 99)
        growth_rate = random.uniform(-2, 15)
        
        # Salvar dados basicos primeiro
        data_to_save = {
            "username": profile['username'],
            "platform": profile['platform'],
            "niche": profile['niche'],
            "city": profile['city'],
            "bio": profile['bio'],
            "link_in_bio": profile['link_in_bio'],
            "has_link_in_bio": bool(profile['link_in_bio']),
            "has_whatsapp": has_whatsapp,
            "sales_language_score": sales_score,
            "followers": profile['followers'],
            "avg_likes": profile['avg_likes'],
            "avg_comments": profile['avg_comments'],
        }
        
        save_influencer(data_to_save)
        
        # Calcular Score Final de Influencia (Affiliate Score)
        temp_data_for_calc = {
            'conversion_potential': conversion_score,
            'engagement_rate': min(100.0, engagement_rate * 10), 
            'authenticity_score': authenticity_score,
            'growth_rate': max(0.0, min(100.0, growth_rate * 5))
        }
        influence_score = rank_engine.calculate_overall_score(temp_data_for_calc)
        
        # Atualizar metrics no DB
        update_scores(
            username=profile['username'],
            engagement=engagement_rate,
            growth=growth_rate,
            conversion=conversion_score,
            authenticity=authenticity_score,
            influence=influence_score,
            sales_score=sales_score
        )
        
    # 3. Gerar Ranking (Focado em Afiliados)
    print("\n[Gerando Ranking de Melhores Afiliados...]")
    all_influencers = get_all_influencers() 
    
    # Usar o novo metodo de ranking especifico
    ranked_list = rank_engine.rank_influencers_for_affiliate(
        all_influencers, 
        min_conversion_score=30.0 # Filtra quem tem pelo menos algum potencial
    )
    
    # 4. Mostrar Top 10 no Terminal
    print("\n" + "="*80)
    print("TOP 10 AFILIADOS POTENCIAIS ENCONTRADOS")
    print("="*80)
    print(f"{'Username':<20} | {'Plat':<7} | {'Wpp':<3} | {'Conv.%':<6} | {'Sales':<5} | {'Score':<5}")
    print("-" * 80)
    
    top_10 = ranked_list[:10]
    for infl in top_10:
        has_wpp = "S" if infl.get('has_whatsapp') else "N"
        conv = infl.get('conversion_potential', 0)
        sales = infl.get('sales_language_score', 0)
        score = infl.get('calculated_ranking_score', 0)
        plat = infl.get('platform', '')[:7] # Truncar para caber
        
        print(f"{infl['username']:<20} | {plat:<7} | {has_wpp:<3} | {conv:>6.1f} | {sales:>5.0f} | {score:>5.1f}")
    
    # 5. Exportar CSV
    print("\nExportando dados...")
    exporter = CSVExporter()
    filepath = exporter.export_ranking(ranked_list)
    
    print(f"\nProcesso concluido! Relatorio salvo em: {filepath}")

if __name__ == "__main__":
    main()
