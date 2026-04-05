#!/usr/bin/env python3
"""
J.A.R.V.I.S. - WEB SEARCH & SELF-IMPROVEMENT
Búsqueda en internet real y capacidad de auto-modificarse
"""

import os
import sys
import json
import time
import re
import hashlib
import requests
import subprocess
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urlparse

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
SEARCH_CACHE = os.path.join(WORKING_DIR, "search_cache.json")
SELF_MOD_LOG = os.path.join(WORKING_DIR, "self_modifications.json")


class WebSearchEngine:
    """Motor de búsqueda en internet real."""
    
    def __init__(self):
        self.cache = self._load_cache()
        self.search_history = []
    
    def _load_cache(self) -> Dict:
        """Cargar caché de búsquedas."""
        if os.path.exists(SEARCH_CACHE):
            with open(SEARCH_CACHE, 'r') as f:
                return json.load(f)
        return {"queries": {}, "last_cleaned": datetime.now().isoformat()}
    
    def _save_cache(self):
        """Guardar caché."""
        with open(SEARCH_CACHE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def search(self, query: str, num_results: int = 10) -> Dict:
        """Buscar en internet con múltiples fuentes."""
        # Verificar caché
        cache_key = hashlib.md5(query.lower().encode()).hexdigest()
        if cache_key in self.cache.get("queries", {}):
            cached = self.cache["queries"][cache_key]
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if (datetime.now() - cached_time).total_seconds() < 3600:  # 1 hora
                return cached["results"]
        
        # Buscar con múltiples fuentes
        results = {
            "query": query,
            "sources": [],
            "summary": "",
            "links": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Fuente 1: DuckDuckGo
        ddg_results = self._search_duckduckgo(query, num_results)
        if ddg_results:
            results["sources"].append("DuckDuckGo")
            results["links"].extend(ddg_results.get("links", []))
        
        # Fuente 2: Wikipedia
        wiki_results = self._search_wikipedia(query)
        if wiki_results:
            results["sources"].append("Wikipedia")
            results["summary"] = wiki_results.get("summary", "")
        
        # Fuente 3: Buscar noticias recientes
        news_results = self._search_news(query)
        if news_results:
            results["sources"].append("News")
            results["news"] = news_results
        
        # Guardar en caché
        if cache_key not in self.cache["queries"]:
            self.cache["queries"][cache_key] = {}
        self.cache["queries"][cache_key] = {
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()
        
        # Guardar historial
        self.search_history.append({
            "query": query,
            "sources": results["sources"],
            "timestamp": datetime.now().isoformat()
        })
        
        return results
    
    def _search_duckduckgo(self, query: str, num: int = 10) -> Optional[Dict]:
        """Buscar en DuckDuckGo."""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                return None
            
            links = []
            html = resp.text
            
            # Extraer resultados
            title_pattern = r'<a class="result__a" href="([^"]+)">([^<]+)</a>'
            snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'
            
            titles = re.findall(title_pattern, html)
            snippets = re.findall(snippet_pattern, html)
            
            for i, (url, title) in enumerate(titles[:num]):
                title = re.sub(r'<[^>]+>', '', title).strip()
                snippet = snippets[i] if i < len(snippets) else ""
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                
                if len(title) > 5 and 'duckduckgo' not in url.lower():
                    links.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "DuckDuckGo"
                    })
            
            return {"links": links} if links else None
        
        except Exception as e:
            return None
    
    def _search_wikipedia(self, query: str) -> Optional[Dict]:
        """Buscar en Wikipedia."""
        try:
            # Extraer término de búsqueda
            search_term = query.split()[0] if query else ""
            if not search_term:
                return None
            
            url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{quote(search_term)}"
            headers = {"User-Agent": "JARVIS/1.0"}
            resp = requests.get(url, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "summary": data.get("extract", ""),
                    "title": data.get("title", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                }
            return None
        except:
            return None
    
    def _search_news(self, query: str) -> Optional[List[Dict]]:
        """Buscar noticias recientes."""
        try:
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=es&gl=ES&ceid=ES:es"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                return None
            
            news = []
            # Parsear RSS simple
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            
            for item in items[:5]:
                title_match = re.search(r'<title>(.*?)</title>', item)
                link_match = re.search(r'<link>(.*?)</link>', item)
                
                if title_match and link_match:
                    news.append({
                        "title": title_match.group(1),
                        "url": link_match.group(1),
                        "source": "Google News"
                    })
            
            return news if news else None
        except:
            return None
    
    def fetch_url(self, url: str) -> Dict:
        """Obtener contenido de una URL."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
            
            # Extraer texto limpio
            content = resp.text[:5000]
            
            # Intentar extraer contenido principal
            text_content = re.sub(r'<[^>]+>', ' ', content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return {
                "success": True,
                "url": url,
                "title": self._extract_title(resp.text),
                "content": text_content[:2000],
                "status_code": resp.status_code
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_title(self, html: str) -> str:
        """Extraer título de HTML."""
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if match:
            return match.group(1)
        return "Sin título"
    
    def format_search_results(self, results: Dict) -> str:
        """Formatear resultados de búsqueda."""
        output = f"🔍 **Resultados para: {results['query']}**\n\n"
        output += f"📡 Fuentes: {', '.join(results['sources'])}\n\n"
        
        if results.get("summary"):
            output += f"📖 **Resumen:**\n{results['summary'][:500]}...\n\n"
        
        if results.get("links"):
            output += f"🔗 **Encontrados ({len(results['links'])}):**\n\n"
            for i, link in enumerate(results['links'][:8], 1):
                output += f"{i}. **{link['title']}**\n"
                output += f"   🔗 {link['url']}\n"
                if link.get('snippet'):
                    output += f"   📝 {link['snippet'][:100]}...\n"
                output += "\n"
        
        if results.get("news"):
            output += f"📰 **Noticias recientes:**\n\n"
            for news in results['news'][:5]:
                output += f"• {news['title']}\n  🔗 {news['url']}\n\n"
        
        return output


class SelfImprovementEngine:
    """Motor de auto-mejora y auto-modificación."""
    
    def __init__(self):
        self.modification_log = self._load_mod_log()
        self.version = self._get_current_version()
    
    def _load_mod_log(self) -> List[Dict]:
        """Cargar historial de modificaciones."""
        if os.path.exists(SELF_MOD_LOG):
            with open(SELF_MOD_LOG, 'r') as f:
                return json.load(f)
        return []
    
    def _save_mod_log(self):
        """Guardar historial."""
        with open(SELF_MOD_LOG, 'w') as f:
            json.dump(self.modification_log, f, indent=2)
    
    def _get_current_version(self) -> str:
        """Obtener versión actual."""
        version_file = os.path.join(WORKING_DIR, "VERSION")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        return "3.0.0"
    
    def _save_version(self, version: str):
        """Guardar versión."""
        version_file = os.path.join(WORKING_DIR, "VERSION")
        with open(version_file, 'w') as f:
            f.write(version)
        self.version = version
    
    def self_update(self) -> Dict:
        """Actualizar J.A.R.V.I.S. desde GitHub."""
        result = {
            "success": False,
            "message": "",
            "changes": []
        }
        
        try:
            # Verificar si hay git
            git_check = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if git_check.returncode != 0:
                result["message"] = "❌ Git no está instalado"
                return result
            
            # Verificar si hay cambios remotos
            os.chdir(WORKING_DIR)
            fetch = subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True, timeout=30)
            
            if fetch.returncode != 0:
                result["message"] = "❌ Error al verificar actualizaciones"
                return result
            
            # Verificar si hay nuevos commits
            status = subprocess.run(
                ["git", "status", "-uno"],
                capture_output=True, text=True, timeout=5
            )
            
            if "Your branch is behind" in status.stdout:
                # Hay actualizaciones
                pull = subprocess.run(
                    ["git", "pull", "origin", "main"],
                    capture_output=True, text=True, timeout=60
                )
                
                if pull.returncode == 0:
                    # Obtener lista de cambios
                    log = subprocess.run(
                        ["git", "log", "--oneline", "-5"],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    changes = log.stdout.strip().split("\n")
                    
                    result["success"] = True
                    result["message"] = f"✅ J.A.R.V.I.S. actualizado correctamente"
                    result["changes"] = changes
                    
                    # Incrementar versión
                    parts = self.version.split(".")
                    parts[-1] = str(int(parts[-1]) + 1)
                    new_version = ".".join(parts)
                    self._save_version(new_version)
                    
                    self.modification_log.append({
                        "type": "update",
                        "version": new_version,
                        "changes": changes,
                        "timestamp": datetime.now().isoformat()
                    })
                    self._save_mod_log()
                else:
                    result["message"] = f"❌ Error al actualizar: {pull.stderr}"
            else:
                result["success"] = True
                result["message"] = "✅ J.A.R.V.I.S. ya está actualizado"
        
        except Exception as e:
            result["message"] = f"❌ Error: {str(e)}"
        
        return result
    
    def self_modify(self, file_path: str, new_content: str, reason: str = "") -> Dict:
        """Modificar un archivo de sí mismo."""
        result = {
            "success": False,
            "message": "",
            "backup_created": False
        }
        
        try:
            full_path = os.path.join(WORKING_DIR, file_path)
            
            if not os.path.exists(full_path):
                result["message"] = f"❌ Archivo no existe: {file_path}"
                return result
            
            # Crear backup
            backup_dir = os.path.join(WORKING_DIR, "self_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(full_path, backup_path)
            result["backup_created"] = True
            
            # Leer contenido actual
            with open(full_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            
            # Escribir nuevo contenido
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            result["success"] = True
            result["message"] = f"✅ {file_path} modificado correctamente"
            result["old_size"] = len(old_content)
            result["new_size"] = len(new_content)
            result["backup_path"] = backup_path
            
            # Registrar modificación
            self.modification_log.append({
                "type": "self_modify",
                "file": file_path,
                "reason": reason,
                "old_size": len(old_content),
                "new_size": len(new_content),
                "backup": backup_path,
                "timestamp": datetime.now().isoformat()
            })
            self._save_mod_log()
        
        except Exception as e:
            result["message"] = f"❌ Error al modificar: {str(e)}"
        
        return result
    
    def self_add_feature(self, feature_name: str, feature_code: str, target_file: str) -> Dict:
        """Agregar una nueva funcionalidad."""
        result = {
            "success": False,
            "message": ""
        }
        
        try:
            target_path = os.path.join(WORKING_DIR, target_file)
            
            if not os.path.exists(target_path):
                result["message"] = f"❌ Archivo destino no existe: {target_file}"
                return result
            
            # Leer archivo actual
            with open(target_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Agregar nueva funcionalidad
            new_content = current_content + "\n\n" + feature_code
            
            # Guardar
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            result["success"] = True
            result["message"] = f"✅ Funcionalidad '{feature_name}' agregada a {target_file}"
            
            self.modification_log.append({
                "type": "add_feature",
                "feature": feature_name,
                "target": target_file,
                "timestamp": datetime.now().isoformat()
            })
            self._save_mod_log()
        
        except Exception as e:
            result["message"] = f"❌ Error: {str(e)}"
        
        return result
    
    def get_modification_history(self, limit: int = 10) -> str:
        """Obtener historial de modificaciones."""
        if not self.modification_log:
            return "📝 No hay modificaciones registradas"
        
        output = "📝 **Historial de Auto-Modificaciones:**\n\n"
        
        for mod in self.modification_log[-limit:]:
            mod_type = mod.get("type", "unknown")
            timestamp = mod.get("timestamp", "unknown")
            
            if mod_type == "update":
                output += f"🔄 **Actualización** ({timestamp[:10]})\n"
                output += f"   Versión: {mod.get('version', '?')}\n"
                for change in mod.get("changes", [])[:3]:
                    output += f"   • {change}\n"
                output += "\n"
            
            elif mod_type == "self_modify":
                output += f"✏️ **Modificación** ({timestamp[:10]})\n"
                output += f"   Archivo: {mod.get('file', '?')}\n"
                output += f"   Razón: {mod.get('reason', 'N/A')}\n\n"
            
            elif mod_type == "add_feature":
                output += f"✨ **Nueva funcionalidad** ({timestamp[:10]})\n"
                output += f"   Feature: {mod.get('feature', '?')}\n"
                output += f"   Archivo: {mod.get('target', '?')}\n\n"
        
        return output
    
    def get_status(self) -> Dict:
        """Obtener estado de auto-mejora."""
        return {
            "version": self.version,
            "total_modifications": len(self.modification_log),
            "recent_modifications": self.modification_log[-5:],
            "can_self_update": True,
            "can_self_modify": True,
            "backup_count": self._count_backups()
        }
    
    def _count_backups(self) -> int:
        """Contar backups."""
        backup_dir = os.path.join(WORKING_DIR, "self_backups")
        if os.path.exists(backup_dir):
            return len(os.listdir(backup_dir))
        return 0


# Instancias globales
web_search = WebSearchEngine()
self_improvement = SelfImprovementEngine()


def test():
    """Probar módulos."""
    print("🌐 Probando Web Search...\n")
    
    results = web_search.search("Python programación")
    print(web_search.format_search_results(results))
    
    print("\n🧠 Probando Self-Improvement...\n")
    
    status = self_improvement.get_status()
    print(f"Versión: {status['version']}")
    print(f"Modificaciones: {status['total_modifications']}")
    print(f"Backups: {status['backup_count']}")
    
    print("\n✅ Prueba completada")


if __name__ == "__main__":
    test()
