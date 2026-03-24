"""
InfluenceHunter AI - Database Connection

Este módulo gerencia a conexão com o banco de dados SQLite.
Funcionalidades:
- Estabelecer conexão com banco de dados SQLite
- Criar tabelas do sistema
- Executar queries
- Realizar operações CRUD
- Gerenciar transações
"""

import sqlite3
from datetime import datetime
import os


def connect_db(db_path="influencehunter.db"):
    """
    Estabelece conexão com o banco de dados SQLite
    
    Args:
        db_path (str): Caminho para o arquivo do banco de dados
        
    Returns:
        sqlite3.Connection: Objeto de conexão com o banco de dados
    """
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        print(f"[OK] Conexao estabelecida com o banco de dados: {db_path}")
        return connection
    except sqlite3.Error as e:
        print(f"[ERRO] Erro ao conectar ao banco de dados: {e}")
        return None


def create_tables(connection):
    """
    Cria as tabelas do sistema no banco de dados
    
    Args:
        connection (sqlite3.Connection): Conexão com o banco de dados
        
    Returns:
        bool: True se as tabelas foram criadas com sucesso
    """
    try:
        cursor = connection.cursor()
        
        # Criar tabela Influencer
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Influencer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                platform TEXT NOT NULL,
                niche TEXT,
                city TEXT,
                bio TEXT,
                link_in_bio TEXT,
                has_link_in_bio BOOLEAN DEFAULT 0,
                has_whatsapp BOOLEAN DEFAULT 0,
                sales_language_score REAL DEFAULT 0.0,
                followers INTEGER DEFAULT 0,
                avg_likes REAL DEFAULT 0.0,
                avg_comments REAL DEFAULT 0.0,
                engagement_rate REAL DEFAULT 0.0,
                growth_rate REAL DEFAULT 0.0,
                conversion_potential REAL DEFAULT 0.0,
                authenticity_score REAL DEFAULT 0.0,
                influence_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, platform)
            )
        """)
        
        connection.commit()
        print("[OK] Tabela 'Influencer' criada com sucesso!")
        return True
        
    except sqlite3.Error as e:
        print(f"[ERRO] Erro ao criar tabelas: {e}")
        return False


class DatabaseConnection:
    """
    Classe para gerenciar conexões e operações com o banco de dados SQLite
    """
    
    def __init__(self, db_path="influencehunter.db"):
        """
        Inicializa a conexão com o banco de dados
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """
        Estabelece conexão com o banco de dados
        
        Returns:
            bool: True se conectado com sucesso
        """
        self.connection = connect_db(self.db_path)
        return self.connection is not None
    
    def disconnect(self):
        """
        Fecha a conexão com o banco de dados
        """
        if self.connection:
            self.connection.close()
            print("[OK] Conexao com o banco de dados fechada")
    
    def execute_query(self, query, params=None):
        """
        Executa uma query no banco de dados
        
        Args:
            query (str): Query SQL a ser executada
            params (tuple): Parâmetros da query
            
        Returns:
            list: Resultados da query
        """
        if not self.connection:
            print("[ERRO] Nao ha conexao ativa com o banco de dados")
            return None
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Se for uma query SELECT, retorna os resultados
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except sqlite3.Error as e:
            print(f"[ERRO] Erro ao executar query: {e}")
            return None
    
    def insert(self, table, data):
        """
        Insere dados em uma tabela
        
        Args:
            table (str): Nome da tabela
            data (dict): Dados a serem inseridos
            
        Returns:
            int: ID do registro inserido ou None em caso de erro
        """
        if not self.connection:
            print("[ERRO] Nao ha conexao ativa com o banco de dados")
            return None
        
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            
            print(f"[OK] Registro inserido na tabela '{table}' com ID: {cursor.lastrowid}")
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"[ERRO] Erro ao inserir dados: {e}")
            return None
    
    def update(self, table, data, condition):
        """
        Atualiza dados em uma tabela
        
        Args:
            table (str): Nome da tabela
            data (dict): Dados a serem atualizados
            condition (str): Condição WHERE (ex: "id = 1")
            
        Returns:
            int: Número de registros atualizados ou None em caso de erro
        """
        if not self.connection:
            print("[ERRO] Nao ha conexao ativa com o banco de dados")
            return None
        
        try:
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            
            print(f"[OK] {cursor.rowcount} registro(s) atualizado(s) na tabela '{table}'")
            return cursor.rowcount
            
        except sqlite3.Error as e:
            print(f"[ERRO] Erro ao atualizar dados: {e}")
            return None
    
    def delete(self, table, condition):
        """
        Deleta dados de uma tabela
        
        Args:
            table (str): Nome da tabela
            condition (str): Condição WHERE (ex: "id = 1")
            
        Returns:
            int: Número de registros deletados ou None em caso de erro
        """
        if not self.connection:
            print("[ERRO] Nao ha conexao ativa com o banco de dados")
            return None
        
        try:
            query = f"DELETE FROM {table} WHERE {condition}"
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            
            print(f"[OK] {cursor.rowcount} registro(s) deletado(s) da tabela '{table}'")
            return cursor.rowcount
            
        except sqlite3.Error as e:
            print(f"[ERRO] Erro ao deletar dados: {e}")
            return None
    
    def select(self, table, columns="*", condition=None, order_by=None, limit=None):
        """
        Seleciona dados de uma tabela
        
        Args:
            table (str): Nome da tabela
            columns (str): Colunas a selecionar (padrão: "*")
            condition (str): Condição WHERE (opcional)
            order_by (str): Ordenação (opcional)
            limit (int): Limite de resultados (opcional)
            
        Returns:
            list: Lista de resultados ou None em caso de erro
        """
        if not self.connection:
            print("[ERRO] Nao ha conexao ativa com o banco de dados")
            return None
        
        try:
            query = f"SELECT {columns} FROM {table}"
            
            if condition:
                query += f" WHERE {condition}"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            return results
            
        except sqlite3.Error as e:
            print(f"[ERRO] Erro ao selecionar dados: {e}")
            return None
