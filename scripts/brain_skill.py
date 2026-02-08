"""
Brain Skill - Sistema de Aprendizaje y Refactorización
D003: Módulo que analiza logs y extrae lecciones aprendidas
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict


class AntigravityBrain:
    """
    Sistema de aprendizaje que analiza logs de ejecución y extrae conocimiento.
    
    Reglas:
    - Validación de Errores: Identifica causa raíz de errores
    - Capitalización: Guarda snippets exitosos
    - No Duplicidad: Consolida conocimiento sin repeticiones
    """
    
    def __init__(self, executions_dir: str = "executions", knowledge_base: str = "KNOWLEDGE_BASE.md"):
        """
        Inicializa el Brain System.
        
        Args:
            executions_dir: Ruta a la carpeta de logs
            knowledge_base: Ruta al archivo de base de conocimientos
        """
        self.executions_dir = Path(executions_dir)
        self.knowledge_base_path = Path(knowledge_base)
        self.lessons = defaultdict(list)
        self.error_patterns = defaultdict(int)
        self.success_patterns = []
        
    def read_logs(self) -> List[Dict[str, any]]:
        """
        Lee todos los archivos .log de la carpeta /executions.
        
        Returns:
            Lista de diccionarios con información de cada log
        """
        logs_data = []
        
        if not self.executions_dir.exists():
            print(f"⚠️  Carpeta {self.executions_dir} no existe")
            return logs_data
        
        log_files = list(self.executions_dir.glob("*.log"))
        
        if not log_files:
            print(f"ℹ️  No se encontraron archivos .log en {self.executions_dir}")
            return logs_data
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                logs_data.append({
                    'filename': log_file.name,
                    'path': str(log_file),
                    'content': content,
                    'lines': content.split('\n')
                })
            except Exception as e:
                print(f"❌ Error leyendo {log_file.name}: {str(e)}")
        
        return logs_data
    
    def analyze_errors(self, logs_data: List[Dict[str, any]]) -> Dict[str, List[str]]:
        """
        Identifica patrones de error en los logs.
        
        Args:
            logs_data: Lista de logs a analizar
            
        Returns:
            Diccionario con patrones de error y ejemplos
        """
        error_analysis = defaultdict(list)
        
        for log in logs_data:
            for line in log['lines']:
                if 'ERROR' in line:
                    # Extraer contexto del error
                    error_msg = line.strip()
                    
                    # Identificar patrones comunes
                    if 'FileNotFoundError' in error_msg or 'no puede encontrar' in error_msg:
                        error_analysis['Archivo no encontrado'].append({
                            'log': log['filename'],
                            'error': error_msg
                        })
                    elif 'PermissionError' in error_msg or 'Access denied' in error_msg:
                        error_analysis['Permisos insuficientes'].append({
                            'log': log['filename'],
                            'error': error_msg
                        })
                    elif 'ModuleNotFoundError' in error_msg or 'No module named' in error_msg:
                        error_analysis['Módulo no encontrado'].append({
                            'log': log['filename'],
                            'error': error_msg
                        })
                    elif 'python' in error_msg.lower() and 'not found' in error_msg.lower():
                        error_analysis['Comando Python incorrecto'].append({
                            'log': log['filename'],
                            'error': error_msg
                        })
                    else:
                        error_analysis['Otros errores'].append({
                            'log': log['filename'],
                            'error': error_msg
                        })
        
        return error_analysis
    
    def extract_success_patterns(self, logs_data: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """
        Extrae patrones de éxito de los logs.
        
        Args:
            logs_data: Lista de logs a analizar
            
        Returns:
            Lista de patrones exitosos
        """
        success_patterns = []
        
        for log in logs_data:
            success_count = sum(1 for line in log['lines'] if 'SUCCESS' in line)
            error_count = sum(1 for line in log['lines'] if 'ERROR' in line)
            
            # Si tiene más éxitos que errores, es un patrón exitoso
            if success_count > 0 and error_count == 0:
                success_patterns.append({
                    'log': log['filename'],
                    'success_count': success_count,
                    'summary': self._extract_summary(log['lines'])
                })
        
        return success_patterns
    
    def _extract_summary(self, lines: List[str]) -> str:
        """
        Extrae un resumen de las operaciones exitosas.
        
        Args:
            lines: Líneas del log
            
        Returns:
            Resumen de operaciones
        """
        success_lines = [line for line in lines if 'SUCCESS' in line or 'INFO' in line]
        if success_lines:
            # Tomar las primeras 3 líneas relevantes
            return " | ".join(success_lines[:3])
        return "Operación completada exitosamente"
    
    def consolidate_knowledge(self, error_analysis: Dict, success_patterns: List) -> Dict:
        """
        Consolida el conocimiento sin duplicados.
        
        Args:
            error_analysis: Análisis de errores
            success_patterns: Patrones de éxito
            
        Returns:
            Conocimiento consolidado
        """
        knowledge = {
            'errors': {},
            'successes': [],
            'recommendations': []
        }
        
        # Consolidar errores (eliminar duplicados)
        for error_type, occurrences in error_analysis.items():
            if occurrences:
                # Tomar solo ejemplos únicos
                unique_errors = []
                seen_messages = set()
                
                for occurrence in occurrences:
                    error_key = occurrence['error'][:100]  # Primeros 100 chars como key
                    if error_key not in seen_messages:
                        seen_messages.add(error_key)
                        unique_errors.append(occurrence)
                
                knowledge['errors'][error_type] = {
                    'count': len(occurrences),
                    'examples': unique_errors[:3]  # Máximo 3 ejemplos
                }
        
        # Consolidar éxitos
        knowledge['successes'] = success_patterns[:5]  # Top 5 éxitos
        
        # Generar recomendaciones
        if 'Comando Python incorrecto' in knowledge['errors']:
            knowledge['recommendations'].append(
                "💡 Usar `py` en lugar de `python` en este entorno Windows"
            )
        
        if 'Archivo no encontrado' in knowledge['errors']:
            knowledge['recommendations'].append(
                "💡 Verificar rutas absolutas y existencia de archivos antes de operaciones"
            )
        
        if 'Módulo no encontrado' in knowledge['errors']:
            knowledge['recommendations'].append(
                "💡 Instalar dependencias con `py -m pip install <módulo>`"
            )
        
        return knowledge
    
    def update_knowledge_base(self, knowledge: Dict):
        """
        Actualiza o crea el archivo KNOWLEDGE_BASE.md.
        
        Args:
            knowledge: Conocimiento consolidado
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# 🧠 BASE DE CONOCIMIENTO ANTIGRAVITY
**Última Actualización:** {timestamp}
**Generado por:** D003_Cerebro

---

## 📊 Resumen de Análisis

- **Tipos de Errores Detectados:** {len(knowledge['errors'])}
- **Patrones Exitosos:** {len(knowledge['successes'])}
- **Recomendaciones Generadas:** {len(knowledge['recommendations'])}

---

## ❌ Errores Identificados

"""
        
        if knowledge['errors']:
            for error_type, data in knowledge['errors'].items():
                content += f"### {error_type}\n"
                content += f"**Ocurrencias:** {data['count']}\n\n"
                content += "**Ejemplos:**\n"
                for i, example in enumerate(data['examples'], 1):
                    content += f"{i}. `{example['log']}`: {example['error'][:150]}...\n"
                content += "\n"
        else:
            content += "*No se detectaron errores en los logs analizados.*\n\n"
        
        content += "---\n\n## ✅ Patrones Exitosos\n\n"
        
        if knowledge['successes']:
            for i, pattern in enumerate(knowledge['successes'], 1):
                content += f"### {i}. {pattern['log']}\n"
                content += f"**Operaciones Exitosas:** {pattern['success_count']}\n"
                content += f"**Resumen:** {pattern['summary'][:200]}...\n\n"
        else:
            content += "*No se detectaron patrones exitosos en los logs analizados.*\n\n"
        
        content += "---\n\n## 💡 Recomendaciones\n\n"
        
        if knowledge['recommendations']:
            for rec in knowledge['recommendations']:
                content += f"- {rec}\n"
        else:
            content += "*No hay recomendaciones en este momento.*\n"
        
        content += "\n---\n\n"
        content += "*Este archivo es generado automáticamente por el Brain System (D003).*\n"
        
        # Guardar archivo
        try:
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Base de conocimiento actualizada: {self.knowledge_base_path}")
        except Exception as e:
            print(f"❌ Error al guardar base de conocimiento: {str(e)}")
    
    def learn(self):
        """
        Ejecuta el ciclo completo de aprendizaje.
        """
        print("\n🧠 BRAIN SYSTEM - Iniciando Análisis de Aprendizaje")
        print("=" * 60)
        
        # 1. Leer logs
        print("\n📖 Paso 1: Leyendo logs de /executions...")
        logs_data = self.read_logs()
        print(f"   ✓ {len(logs_data)} archivos de log encontrados")
        
        # 2. Analizar errores
        print("\n🔍 Paso 2: Analizando patrones de error...")
        error_analysis = self.analyze_errors(logs_data)
        total_errors = sum(len(errors) for errors in error_analysis.values())
        print(f"   ✓ {total_errors} errores identificados en {len(error_analysis)} categorías")
        
        # 3. Extraer éxitos
        print("\n🎯 Paso 3: Extrayendo patrones exitosos...")
        success_patterns = self.extract_success_patterns(logs_data)
        print(f"   ✓ {len(success_patterns)} patrones exitosos detectados")
        
        # 4. Consolidar conocimiento
        print("\n🔄 Paso 4: Consolidando conocimiento...")
        knowledge = self.consolidate_knowledge(error_analysis, success_patterns)
        print(f"   ✓ Conocimiento consolidado sin duplicados")
        
        # 5. Actualizar base de conocimiento
        print("\n💾 Paso 5: Actualizando KNOWLEDGE_BASE.md...")
        self.update_knowledge_base(knowledge)
        
        print("\n" + "=" * 60)
        print("✅ Ciclo de aprendizaje completado\n")
        
        return knowledge


def create_brain() -> AntigravityBrain:
    """
    Factory function para crear una instancia del Brain System.
    
    Returns:
        Instancia de AntigravityBrain
    """
    return AntigravityBrain()
