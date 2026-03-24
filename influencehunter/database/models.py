"""
InfluenceHunter AI - Database Models

Este módulo contém a lógica de negócios para manipulação dos dados de influenciadores.
Funcionalidades:
- Salvar influenciadores (Criar/Atualizar)
- Recuperar todos os influenciadores
- Atualizar scores e métricas
"""

from typing import List, Dict, Optional, Union
import sqlite3
from .connection import DatabaseConnection

# Configuração padrão do caminho do banco (pode ser movido para config.py)
DB_PATH = "influencehunter.db"


def save_influencer(data: Dict) -> Optional[int]:
    """
    Salva um influenciador no banco de dados. 
    Se o influenciador (username + platform) já existir, atualiza os dados.
    Caso contrário, cria um novo registro.

    Args:
        data (dict): Dicionário contendo os dados do influenciador.
                     Campos obrigatórios: 'username', 'platform'.

    Returns:
        int: ID do influenciador salvo (ou atualizado), ou None em caso de erro.
    """
    # Validação básica
    if not data.get('username') or not data.get('platform'):
        print("❌ Erro: 'username' e 'platform' são obrigatórios.")
        return None

    db = DatabaseConnection(DB_PATH)
    if not db.connect():
        return None

    try:
        # Verifica se já existe
        username = data['username']
        platform = data['platform']
        
        existing = db.select(
            table="Influencer",
            columns="id",
            condition=f"username = '{username}' AND platform = '{platform}'",
            limit=1
        )

        if existing:
            # Atualizar
            influencer_id = existing[0]['id']
            # Remove campos que não devem ser atualizados na edição básica se necessário,
            # mas aqui assumimos que 'data' tem o que queremos atualizar.
            # Removemos chaves que não existem na tabela se necessário, 
            # mas assumiremos que o chamador passa dados corretos ou o DB ignora/dá erro.
            # Importante: DatabaseConnection.update espera um dicionário mapeado para colunas.
            
            # Prevenir atualização do ID ou created_at via save_influencer se vier no dict
            update_data = data.copy()
            update_data.pop('id', None)
            update_data.pop('created_at', None)
            
            rows_affected = db.update(
                table="Influencer",
                data=update_data,
                condition=f"id = {influencer_id}"
            )
            
            if rows_affected is not None:
                print(f"[ATUALIZADO] Influenciador '{username}' atualizado.")
                return influencer_id
            return None
        else:
            # Inserir novo
            new_id = db.insert("Influencer", data)
            if new_id:
                print(f"[NOVO] Novo influenciador '{username}' cadastrado.")
            return new_id

    except Exception as e:
        print(f"[ERRO] Erro em save_influencer: {e}")
        return None
    finally:
        db.disconnect()


def get_all_influencers() -> List[sqlite3.Row]:
    """
    Recupera todos os influenciadores cadastrados no banco de dados.

    Returns:
        list: Lista de registros (sqlite3.Row) dos influenciadores.
              Retorna lista vazia em caso de erro ou nenhum registro.
    """
    db = DatabaseConnection(DB_PATH)
    if not db.connect():
        return []

    try:
        results = db.select(table="Influencer", order_by="influence_score DESC")
        if results:
            print(f"[INFO] {len(results)} influenciadores encontrados.")
            return results
        return []
    except Exception as e:
        print(f"[ERRO] Erro em get_all_influencers: {e}")
        return []
    finally:
        db.disconnect()


def update_scores(username: str, engagement: float, growth: float, conversion: float, authenticity: float, influence: float, sales_score: float = 0.0) -> bool:
    """
    Atualiza os scores e métricas de um influenciador específico.

    Args:
        username (str): Nome de usuário do influenciador.
        engagement (float): Nova taxa de engajamento.
        growth (float): Nova taxa de crescimento.
        conversion (float): Novo potencial de conversão.
        authenticity (float): Novo score de autenticidade.
        influence (float): Novo Score de Influência geral.
        sales_score (float): Score da linguagem de vendas (0-100).

    Returns:
        bool: True se a atualização foi bem sucedida, False caso contrário.
    """
    if not username:
        print("[ERRO] 'username' e obrigatorio para atualizar scores.")
        return False

    db = DatabaseConnection(DB_PATH)
    if not db.connect():
        return False

    try:
        # Prepara os dados para atualização
        score_data = {
            "engagement_rate": engagement,
            "growth_rate": growth,
            "conversion_potential": conversion,
            "sales_language_score": sales_score,
            "authenticity_score": authenticity,
            "influence_score": influence
        }

        # Atualiza baseado no username. 
        rows = db.update(
            table="Influencer",
            data=score_data,
            condition=f"username = '{username}'"
        )
        
        if rows and rows > 0:
            print(f"[ATUALIZADO] Scores atualizados para '{username}'.")
            return True
        else:
            print(f"[AVISO] Nenhuma atualizacao feita para '{username}'. Usuario nao encontrado?")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar scores: {e}")
        return False
    finally:
        db.disconnect()

