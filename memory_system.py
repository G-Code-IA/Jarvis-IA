#!/usr/bin/env python3
"""
J.A.R.V.I.S. - SISTEMA DE MEMORIA Y APRENDIZAJE
Memoria persistente, evolución y auto-mejora
"""

import os
import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from pathlib import Path

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
MEMORY_DB = os.path.join(WORKING_DIR, "memory.db")
LEARNING_DB = os.path.join(WORKING_DIR, "learning.db")


# ==================== BASE DE DATOS DE MEMORIA ====================

class MemoryDatabase:
    """Base de datos de memoria persistente."""
    
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(MEMORY_DB)
        c = conn.cursor()
        
        # Memorias a largo plazo
        c.execute('''CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            content TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            access_count INTEGER DEFAULT 0,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP
        )''')
        
        # Memorias de conversación
        c.execute('''CREATE TABLE IF NOT EXISTS conversation_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            response TEXT,
            sentiment TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Preferencias de usuario
        c.execute('''CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            category TEXT,
            updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Conocimiento aprendido
        c.execute('''CREATE TABLE IF NOT EXISTS learned_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            content TEXT,
            confidence REAL DEFAULT 0.5,
            source TEXT,
            verified BOOLEAN DEFAULT 0,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Contexto actual
        c.execute('''CREATE TABLE IF NOT EXISTS current_context (
            key TEXT PRIMARY KEY,
            value TEXT,
            expires TIMESTAMP
        )''')
        
        # Índice vectorial simple (para búsqueda semántica)
        c.execute('''CREATE TABLE IF NOT EXISTS memory_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id INTEGER,
            embedding TEXT,
            FOREIGN KEY (memory_id) REFERENCES long_term_memory(id)
        )''')
        
        conn.commit()
        conn.close()
    
    def execute(self, query: str, params: tuple = None) -> List:
        conn = sqlite3.connect(MEMORY_DB)
        c = conn.cursor()
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        result = c.fetchall()
        conn.commit()
        conn.close()
        return result
    
    def execute_many(self, query: str, params_list: list):
        conn = sqlite3.connect(MEMORY_DB)
        c = conn.cursor()
        c.executemany(query, params_list)
        conn.commit()
        conn.close()


# ==================== SISTEMA DE MEMORIA ====================

class MemorySystem:
    """Sistema de memoria inspirado en cerebro humano."""
    
    def __init__(self):
        self.db = MemoryDatabase()
        self.short_term = []  # Memoria a corto plazo (RAM)
        self.working_context = {}  # Contexto de trabajo actual
        self.max_short_term = 100
    
    def add_short_term(self, content: str, category: str = "general"):
        """Agregar a memoria a corto plazo."""
        self.short_term.append({
            "content": content,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limitar tamaño
        if len(self.short_term) > self.max_short_term:
            # Consolidar memorias antiguas a largo plazo
            old_memory = self.short_term.pop(0)
            self.consolidate_to_long_term(old_memory["content"], old_memory["category"])
    
    def consolidate_to_long_term(self, content: str, category: str, importance: float = 0.5):
        """Consolidar memoria de corto a largo plazo."""
        self.db.execute(
            "INSERT INTO long_term_memory (category, content, importance, last_accessed) VALUES (?, ?, ?, ?)",
            (category, content, importance, datetime.now().isoformat())
        )
    
    def get_long_term(self, category: str = None, limit: int = 50) -> List[Dict]:
        """Obtener memorias a largo plazo."""
        if category:
            results = self.db.execute(
                "SELECT * FROM long_term_memory WHERE category = ? ORDER BY last_accessed DESC LIMIT ?",
                (category, limit)
            )
        else:
            results = self.db.execute(
                "SELECT * FROM long_term_memory ORDER BY importance DESC, last_accessed DESC LIMIT ?",
                (limit,)
            )
        
        return [dict(zip(["id", "category", "content", "importance", "access_count", "created", "last_accessed"], r)) 
                for r in results]
    
    def search_memory(self, query: str, limit: int = 10) -> List[Dict]:
        """Buscar memorias por contenido (búsqueda semántica simple)."""
        results = self.db.execute(
            """SELECT * FROM long_term_memory 
               WHERE content LIKE ? OR category LIKE ?
               ORDER BY importance DESC, access_count DESC 
               LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit)
        )
        
        # Actualizar contador de acceso
        for r in results:
            self.db.execute(
                "UPDATE long_term_memory SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
                (datetime.now().isoformat(), r[0])
            )
        
        return [dict(zip(["id", "category", "content", "importance", "access_count", "created", "last_accessed"], r)) 
                for r in results]
    
    def add_conversation(self, user_id: int, message: str, response: str, sentiment: str = "neutral"):
        """Guardar conversación en memoria."""
        self.db.execute(
            "INSERT INTO conversation_memory (user_id, message, response, sentiment) VALUES (?, ?, ?, ?)",
            (user_id, message, response, sentiment)
        )
        
        # Extraer información importante para memoria a largo plazo
        self.extract_important_info(message, response)
    
    def extract_important_info(self, message: str, response: str):
        """Extraer información importante de conversaciones."""
        # Palabras clave que indican información importante
        important_keywords = [
            "prefiero", "me gusta", "no me gusta", "recuerda", "importante",
            "siempre", "nunca", "odio", "amo", "quiero", "necesito",
            "nombre", "edad", "trabajo", "casa", "familia"
        ]
        
        text = (message + " " + response).lower()
        
        for keyword in important_keywords:
            if keyword in text:
                self.consolidate_to_long_term(
                    f"{message} -> {response}",
                    f"user_preference_{keyword}",
                    importance=0.8
                )
                break
    
    def get_conversation_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Obtener historial de conversaciones."""
        results = self.db.execute(
            "SELECT * FROM conversation_memory WHERE user_id = ? ORDER BY created DESC LIMIT ?",
            (user_id, limit)
        )
        
        return [dict(zip(["id", "user_id", "message", "response", "sentiment", "created"], r)) 
                for r in results]
    
    def set_preference(self, key: str, value: str, category: str = "general"):
        """Guardar preferencia de usuario."""
        self.db.execute(
            """INSERT OR REPLACE INTO user_preferences (key, value, category, updated) 
               VALUES (?, ?, ?, ?)""",
            (key, value, category, datetime.now().isoformat())
        )
    
    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        """Obtener preferencia de usuario."""
        results = self.db.execute(
            "SELECT value FROM user_preferences WHERE key = ?",
            (key,)
        )
        return results[0][0] if results else default
    
    def get_all_preferences(self) -> Dict[str, str]:
        """Obtener todas las preferencias."""
        results = self.db.execute("SELECT key, value, category FROM user_preferences")
        return {r[0]: {"value": r[1], "category": r[2]} for r in results}
    
    def add_knowledge(self, topic: str, content: str, source: str = "user", confidence: float = 0.5):
        """Agregar conocimiento aprendido."""
        self.db.execute(
            """INSERT INTO learned_knowledge (topic, content, confidence, source) 
               VALUES (?, ?, ?, ?)""",
            (topic, content, confidence, source)
        )
    
    def get_knowledge(self, topic: str) -> List[Dict]:
        """Obtener conocimiento sobre un tema."""
        results = self.db.execute(
            "SELECT * FROM learned_knowledge WHERE topic LIKE ? ORDER BY confidence DESC",
            (f"%{topic}%",)
        )
        
        return [dict(zip(["id", "topic", "content", "confidence", "source", "verified", "created"], r)) 
                for r in results]
    
    def verify_knowledge(self, knowledge_id: int):
        """Verificar conocimiento como correcto."""
        self.db.execute(
            "UPDATE learned_knowledge SET verified = 1, confidence = confidence + 0.1 WHERE id = ?",
            (knowledge_id,)
        )
    
    def set_context(self, key: str, value: str, expires_in_minutes: int = 60):
        """Establecer contexto temporal."""
        expires = (datetime.now() + timedelta(minutes=expires_in_minutes)).isoformat()
        self.db.execute(
            """INSERT OR REPLACE INTO current_context (key, value, expires) 
               VALUES (?, ?, ?)""",
            (key, value, expires)
        )
    
    def get_context(self, key: str) -> Optional[str]:
        """Obtener contexto temporal."""
        results = self.db.execute(
            "SELECT value, expires FROM current_context WHERE key = ?",
            (key,)
        )
        
        if results:
            value, expires = results[0]
            if datetime.fromisoformat(expires) > datetime.now():
                return value
            else:
                # Expirado
                self.db.execute("DELETE FROM current_context WHERE key = ?", (key,))
        return None
    
    def get_context_summary(self) -> Dict:
        """Obtener resumen de contexto actual."""
        results = self.db.execute("SELECT key, value FROM current_context WHERE expires > ?", 
                                  (datetime.now().isoformat(),))
        return {r[0]: r[1] for r in results}
    
    def clear_expired_context(self):
        """Limpiar contexto expirado."""
        self.db.execute("DELETE FROM current_context WHERE expires < ?", 
                        (datetime.now().isoformat(),))
    
    def get_memory_stats(self) -> Dict:
        """Obtener estadísticas de memoria."""
        stats = {}
        
        # Contar memorias
        result = self.db.execute("SELECT COUNT(*) FROM long_term_memory")
        stats["long_term_count"] = result[0][0] if result else 0
        
        result = self.db.execute("SELECT COUNT(*) FROM conversation_memory")
        stats["conversation_count"] = result[0][0] if result else 0
        
        result = self.db.execute("SELECT COUNT(*) FROM learned_knowledge")
        stats["knowledge_count"] = result[0][0] if result else 0
        
        result = self.db.execute("SELECT COUNT(*) FROM user_preferences")
        stats["preferences_count"] = result[0][0] if result else 0
        
        stats["short_term_count"] = len(self.short_term)
        
        return stats
    
    def export_memory(self, filepath: str = None):
        """Exportar memoria a archivo JSON."""
        if not filepath:
            filepath = os.path.join(WORKING_DIR, f"memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "long_term_memory": self.get_long_term(limit=1000),
            "preferences": self.get_all_preferences(),
            "stats": self.get_memory_stats()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def import_memory(self, filepath: str):
        """Importar memoria desde archivo JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # Importar preferencias
        for key, data in import_data.get("preferences", {}).items():
            if isinstance(data, dict):
                self.set_preference(key, data.get("value", ""), data.get("category", "general"))
            else:
                self.set_preference(key, str(data))
        
        return f"Memoria importada desde {filepath}"


# ==================== SISTEMA DE APRENDIZAJE ====================

class LearningSystem:
    """Sistema de aprendizaje y auto-mejora."""
    
    def __init__(self):
        self.memory = MemorySystem()
        self.performance_log = []
        self.init_learning_db()
    
    def init_learning_db(self):
        conn = sqlite3.connect(LEARNING_DB)
        c = conn.cursor()
        
        # Registro de comandos ejecutados
        c.execute('''CREATE TABLE IF NOT EXISTS command_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            success BOOLEAN,
            execution_time REAL,
            user_feedback TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Patrones aprendidos
        c.execute('''CREATE TABLE IF NOT EXISTS learned_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            pattern TEXT,
            response TEXT,
            success_rate REAL DEFAULT 0.5,
            usage_count INTEGER DEFAULT 0,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Optimizaciones aplicadas
        c.execute('''CREATE TABLE IF NOT EXISTS optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component TEXT,
            description TEXT,
            improvement REAL,
            applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
    
    def log_command(self, command: str, success: bool, execution_time: float, user_feedback: str = None):
        """Registrar ejecución de comando."""
        conn = sqlite3.connect(LEARNING_DB)
        c = conn.cursor()
        c.execute(
            """INSERT INTO command_log (command, success, execution_time, user_feedback) 
               VALUES (?, ?, ?, ?)""",
            (command, success, execution_time, user_feedback)
        )
        conn.commit()
        conn.close()
        
        # Analizar si hay patrones que aprender
        self.analyze_patterns(command, success)
    
    def analyze_patterns(self, command: str, success: bool):
        """Analizar patrones de comandos exitosos."""
        if success:
            # Extraer tipo de comando
            command_type = self._extract_command_type(command)
            
            conn = sqlite3.connect(LEARNING_DB)
            c = conn.cursor()
            
            # Verificar si ya existe patrón similar
            c.execute(
                "SELECT id, success_rate, usage_count FROM learned_patterns WHERE pattern_type = ?",
                (command_type,)
            )
            result = c.fetchone()
            
            if result:
                # Actualizar patrón existente
                pattern_id, success_rate, usage_count = result
                new_success_rate = (success_rate * usage_count + 1.0) / (usage_count + 1)
                c.execute(
                    """UPDATE learned_patterns 
                       SET success_rate = ?, usage_count = usage_count + 1 
                       WHERE id = ?""",
                    (new_success_rate, pattern_id)
                )
            else:
                # Crear nuevo patrón
                c.execute(
                    """INSERT INTO learned_patterns (pattern_type, pattern, response, success_rate, usage_count) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (command_type, command, "success", 1.0, 1)
                )
            
            conn.commit()
            conn.close()
    
    def _extract_command_type(self, command: str) -> str:
        """Extraer tipo de comando."""
        command_lower = command.lower()
        
        if any(x in command_lower for x in ["batería", "battery"]):
            return "system_battery"
        elif any(x in command_lower for x in ["archivo", "file"]):
            return "file_operation"
        elif any(x in command_lower for x in ["busca", "search"]):
            return "web_search"
        elif any(x in command_lower for x in ["crea", "create"]):
            return "create_operation"
        elif any(x in command_lower for x in ["analiza", "analyze"]):
            return "analysis_operation"
        else:
            return "general"
    
    def get_successful_patterns(self, pattern_type: str = None) -> List[Dict]:
        """Obtener patrones exitosos."""
        conn = sqlite3.connect(LEARNING_DB)
        c = conn.cursor()
        
        if pattern_type:
            c.execute(
                "SELECT * FROM learned_patterns WHERE pattern_type = ? AND success_rate > 0.7 ORDER BY success_rate DESC",
                (pattern_type,)
            )
        else:
            c.execute(
                "SELECT * FROM learned_patterns WHERE success_rate > 0.7 ORDER BY success_rate DESC LIMIT 20"
            )
        
        results = c.fetchall()
        conn.close()
        
        return [dict(zip(["id", "pattern_type", "pattern", "response", "success_rate", "usage_count", "created"], r)) 
                for r in results]
    
    def add_optimization(self, component: str, description: str, improvement: float):
        """Registrar optimización aplicada."""
        conn = sqlite3.connect(LEARNING_DB)
        c = conn.cursor()
        c.execute(
            """INSERT INTO optimizations (component, description, improvement) 
               VALUES (?, ?, ?)""",
            (component, description, improvement)
        )
        conn.commit()
        conn.close()
    
    def get_optimization_history(self, limit: int = 20) -> List[Dict]:
        """Obtener historial de optimizaciones."""
        conn = sqlite3.connect(LEARNING_DB)
        c = conn.cursor()
        c.execute(
            "SELECT * FROM optimizations ORDER BY applied DESC LIMIT ?",
            (limit,)
        )
        results = c.fetchall()
        conn.close()
        
        return [dict(zip(["id", "component", "description", "improvement", "applied"], r)) 
                for r in results]
    
    def get_performance_stats(self) -> Dict:
        """Obtener estadísticas de rendimiento."""
        conn = sqlite3.connect(LEARNING_DB)
        c = conn.cursor()
        
        stats = {}
        
        # Total comandos
        c.execute("SELECT COUNT(*) FROM command_log")
        stats["total_commands"] = c.fetchone()[0]
        
        # Comandos exitosos
        c.execute("SELECT COUNT(*) FROM command_log WHERE success = 1")
        stats["successful_commands"] = c.fetchone()[0]
        
        # Tasa de éxito
        if stats["total_commands"] > 0:
            stats["success_rate"] = stats["successful_commands"] / stats["total_commands"]
        else:
            stats["success_rate"] = 0
        
        # Tiempo promedio de ejecución
        c.execute("SELECT AVG(execution_time) FROM command_log")
        stats["avg_execution_time"] = c.fetchone()[0] or 0
        
        # Patrones aprendidos
        c.execute("SELECT COUNT(*) FROM learned_patterns")
        stats["learned_patterns"] = c.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def suggest_improvements(self) -> List[str]:
        """Sugerir mejoras basadas en el aprendizaje."""
        suggestions = []
        stats = self.get_performance_stats()
        
        # Sugerencias basadas en tasa de éxito
        if stats["success_rate"] < 0.8:
            suggestions.append("⚠️ Tasa de éxito baja ({:.1%}). Revisar comandos fallidos.".format(stats["success_rate"]))
        
        # Sugerencias basadas en tiempo de ejecución
        if stats["avg_execution_time"] > 10:
            suggestions.append("⏱️ Tiempo promedio alto ({:.1f}s). Considerar optimizar.".format(stats["avg_execution_time"]))
        
        # Sugerencias basadas en patrones
        patterns = self.get_successful_patterns()
        if len(patterns) < 5:
            suggestions.append("📚 Pocos patrones aprendidos. Más uso mejorará las sugerencias.")
        
        return suggestions
    
    def auto_optimize(self) -> List[str]:
        """Aplicar auto-optimizaciones basadas en aprendizaje."""
        optimizations_applied = []
        
        # Analizar comandos lentos
        conn = sqlite3.connect(LEARNING_DB)
        c = conn.cursor()
        c.execute(
            """SELECT command, AVG(execution_time) as avg_time 
               FROM command_log 
               WHERE execution_time > 5
               GROUP BY command 
               HAVING COUNT(*) > 3
               ORDER BY avg_time DESC 
               LIMIT 5"""
        )
        slow_commands = c.fetchall()
        conn.close()
        
        for command, avg_time in slow_commands:
            optimization = f"Comando '{command[:50]}...' promedia {avg_time:.1f}s - Considerar caché o optimización"
            self.add_optimization("command_performance", optimization, avg_time * 0.3)
            optimizations_applied.append(optimization)
        
        return optimizations_applied
    
    def export_learning(self, filepath: str = None):
        """Exportar datos de aprendizaje."""
        if not filepath:
            filepath = os.path.join(WORKING_DIR, f"learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "stats": self.get_performance_stats(),
            "patterns": self.get_successful_patterns(),
            "optimizations": self.get_optimization_history()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath


# ==================== INSTANCIAS GLOBALES ====================

memory_system = MemorySystem()
learning_system = LearningSystem()


def test_memory():
    """Probar sistema de memoria."""
    print("🧠 Probando sistema de memoria...")
    
    # Agregar memorias
    memory_system.add_short_term("El usuario prefiere Python", "preference")
    memory_system.consolidate_to_long_term("Usuario usa Android/Termux", "user_info", 0.9)
    
    # Guardar preferencia
    memory_system.set_preference("language", "español", "user")
    memory_system.set_preference("favorite_language", "python", "coding")
    
    # Agregar conversación
    memory_system.add_conversation(8406954800, "¿Cuál es mi lenguaje favorito?", "Python", "positive")
    
    # Agregar conocimiento
    learning_system.add_knowledge("python", "Python es bueno para IA", "user", 0.8)
    
    # Registrar comando
    learning_system.log_command("batería", True, 0.5, "positive")
    learning_system.log_command("crear archivo", True, 1.2, "positive")
    
    # Mostrar estadísticas
    print("\n📊 Estadísticas de Memoria:")
    stats = memory_system.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n📊 Estadísticas de Aprendizaje:")
    stats = learning_system.get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🎯 Preferencias:")
    prefs = memory_system.get_all_preferences()
    for key, data in prefs.items():
        print(f"  {key}: {data}")
    
    print("\n✅ Sistema de memoria probado")


if __name__ == "__main__":
    test_memory()
