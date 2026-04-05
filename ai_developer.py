#!/usr/bin/env python3
"""
J.A.R.V.I.S. - MÓDULO DE DESARROLLADOR DE IA
Capaz de crear, analizar y optimizar código en múltiples lenguajes
"""

import os
import re
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
PROJECTS_DIR = os.path.join(WORKING_DIR, "projects")
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_TIMEOUT = 60

# Lenguajes soportados
LANGUAGES = {
    "python": {"ext": ".py", "run": "python", "analyze": True},
    "cpp": {"ext": ".cpp", "run": "g++", "analyze": True},
    "c": {"ext": ".c", "run": "gcc", "analyze": True},
    "rust": {"ext": ".rs", "run": "rustc", "analyze": True},
    "javascript": {"ext": ".js", "run": "node", "analyze": True},
    "typescript": {"ext": ".ts", "run": "tsc", "analyze": True},
    "java": {"ext": ".java", "run": "javac", "analyze": True},
    "go": {"ext": ".go", "run": "go run", "analyze": True},
    "ruby": {"ext": ".rb", "run": "ruby", "analyze": True},
    "php": {"ext": ".php", "run": "php", "analyze": True},
    "swift": {"ext": ".swift", "run": "swift", "analyze": True},
    "kotlin": {"ext": ".kt", "run": "kotlinc", "analyze": True},
    "lua": {"ext": ".lua", "run": "lua", "analyze": True},
    "bash": {"ext": ".sh", "run": "bash", "analyze": True},
}


class CodeAnalyzer:
    """Analizador de código multi-lenguaje."""
    
    @staticmethod
    def analyze_file(file_path: str, language: str) -> Dict:
        """Analizar un archivo de código."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Métricas básicas
            metrics = {
                "file": file_path,
                "language": language,
                "lines": len(lines),
                "code_lines": sum(1 for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('#')),
                "comment_lines": sum(1 for l in lines if l.strip().startswith('//') or l.strip().startswith('#') or l.strip().startswith('/*')),
                "blank_lines": sum(1 for l in lines if not l.strip()),
                "functions": 0,
                "classes": 0,
                "imports": 0,
            }
            
            # Contar funciones y clases según lenguaje
            if language in ["python"]:
                metrics["functions"] = len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
                metrics["classes"] = len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
                metrics["imports"] = len(re.findall(r'^(?:import|from)\s+', content, re.MULTILINE))
            
            elif language in ["cpp", "c"]:
                metrics["functions"] = len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*\{', content))
                metrics["classes"] = len(re.findall(r'(?:class|struct)\s+\w+', content))
                metrics["imports"] = len(re.findall(r'#include', content))
            
            elif language in ["javascript", "typescript"]:
                metrics["functions"] = len(re.findall(r'(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?\([^)]*\))', content))
                metrics["classes"] = len(re.findall(r'class\s+\w+', content))
                metrics["imports"] = len(re.findall(r'(?:import|require\()', content))
            
            elif language in ["rust"]:
                metrics["functions"] = len(re.findall(r'fn\s+\w+', content))
                metrics["classes"] = len(re.findall(r'(?:struct|enum|impl)\s+\w+', content))
                metrics["imports"] = len(re.findall(r'use\s+', content))
            
            elif language in ["java"]:
                metrics["functions"] = len(re.findall(r'(?:public|private|protected)\s+\w+\s+\w+\s*\(', content))
                metrics["classes"] = len(re.findall(r'(?:class|interface)\s+\w+', content))
                metrics["imports"] = len(re.findall(r'^import\s+', content, re.MULTILINE))
            
            return metrics
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def detect_language(file_path: str) -> Optional[str]:
        """Detectar lenguaje por extensión."""
        ext = Path(file_path).suffix.lower()
        for lang, info in LANGUAGES.items():
            if info["ext"] == ext:
                return lang
        return None
    
    @staticmethod
    def find_issues(file_path: str, language: str) -> List[str]:
        """Encontrar problemas potenciales en el código."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Problemas comunes
            if len(content) > 100000:
                issues.append("⚠️ Archivo muy grande (>100KB)")
            
            if len(lines) > 1000:
                issues.append("⚠️ Archivo muy largo (>1000 líneas)")
            
            # Líneas muy largas
            long_lines = [i+1 for i, l in enumerate(lines) if len(l) > 120]
            if long_lines:
                issues.append(f"⚠️ {len(long_lines)} líneas muy largas (>120 chars): líneas {long_lines[:5]}...")
            
            # Funciones muy largas (simple heuristic)
            if language == "python":
                # Detectar funciones sin docstring
                func_matches = re.finditer(r'^\s*def\s+(\w+)\s*\([^)]*\)\s*:', content, re.MULTILINE)
                for match in func_matches:
                    func_name = match.group(1)
                    start = match.end()
                    next_chars = content[start:start+50].replace('\n', ' ').strip()
                    if not next_chars.startswith('"""') and not next_chars.startswith("'''"):
                        issues.append(f"⚠️ Función '{func_name}' sin docstring")
            
            # Variables no usadas (simple)
            if language in ["python", "javascript"]:
                # Esto es una simplificación
                pass
            
            # TODOs y FIXMEs
            todos = re.findall(r'(?:TODO|FIXME|XXX|HACK):\s*(.+)', content, re.IGNORECASE)
            if todos:
                issues.append(f"📝 {len(todos)} comentarios TODO/FIXMEX")
            
            # Código comentado extenso
            commented = re.findall(r'(?://|#|/\*).{50,}', content)
            if len(commented) > 10:
                issues.append(f"⚠️ Mucho código comentado ({len(commented)} bloques)")
            
        except Exception as e:
            issues.append(f"❌ Error al analizar: {str(e)}")
        
        return issues
    
    @staticmethod
    def get_complexity(content: str, language: str) -> str:
        """Estimar complejidad ciclomática (simplificada)."""
        # Contar estructuras de control
        branches = len(re.findall(r'\b(?:if|else|elif|for|while|case|catch|except|and|or)\b', content))
        functions = len(re.findall(r'\b(?:def|function|fn|func)\b', content))
        
        complexity = branches + (functions * 2)
        
        if complexity < 10:
            return f"Baja ({complexity})"
        elif complexity < 30:
            return f"Media ({complexity})"
        else:
            return f"Alta ({complexity})"


class CodeOptimizer:
    """Optimizador de código con IA."""
    
    @staticmethod
    def optimize_code(code: str, language: str, goal: str = "performance") -> str:
        """Optimizar código usando IA."""
        prompt = f"""Eres un experto optimizador de código {language}.

Objetivo: {goal}

Código original:
```{language}
{code[:3000]}
```

Proporciona SOLO el código optimizado, sin explicaciones.
Usa las mejores prácticas de optimización para {language}.
Mantén la misma funcionalidad pero más eficiente."""

        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 2000,
                }
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=OLLAMA_TIMEOUT)
            resp.raise_for_status()
            return resp.json().get("response", "No se pudo optimizar")
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def refactor_code(code: str, language: str, instruction: str) -> str:
        """Refactorizar código según instrucciones."""
        prompt = f"""Eres un experto refactorizando código {language}.

Instrucción: {instruction}

Código original:
```{language}
{code[:3000]}
```

Proporciona SOLO el código refactorizado, sin explicaciones."""

        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.4, "num_predict": 2000}
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=OLLAMA_TIMEOUT)
            return resp.json().get("response", "No se pudo refactorizar")
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def add_types(code: str, language: str) -> str:
        """Agregar tipado al código."""
        if language == "python":
            prompt = f"""Agrega type hints a este código Python:

```python
{code[:2000]}
```

Solo devuelve el código con type hints, sin explicaciones."""
        elif language == "javascript":
            prompt = f"""Convierte este JavaScript a TypeScript con tipos completos:

```javascript
{code[:2000]}
```

Solo devuelve el código TypeScript, sin explicaciones."""
        else:
            return f"❌ Tipado automático no disponible para {language}"
        
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 1500}
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=OLLAMA_TIMEOUT)
            return resp.json().get("response", "No se pudo agregar tipado")
        
        except Exception as e:
            return f"❌ Error: {str(e)}"


class ProjectGenerator:
    """Generador de proyectos completos."""
    
    @staticmethod
    def create_project_structure(name: str, project_type: str, language: str) -> Dict[str, str]:
        """Crear estructura de archivos para un proyecto."""
        structures = {
            "minecraft_clone": {
                "cpp": {
                    "CMakeLists.txt": ProjectGenerator._cmake_minecraft(),
                    "src/main.cpp": ProjectGenerator._main_cpp(),
                    "src/world.hpp": ProjectGenerator._world_hpp(),
                    "src/world.cpp": ProjectGenerator._world_cpp(),
                    "src/renderer.hpp": ProjectGenerator._renderer_hpp(),
                    "src/renderer.cpp": ProjectGenerator._renderer_cpp(),
                    "src/player.hpp": ProjectGenerator._player_hpp(),
                    "src/player.cpp": ProjectGenerator._player_cpp(),
                    "README.md": ProjectGenerator._readme_minecraft(),
                }
            },
            "web_app": {
                "python": {
                    "main.py": ProjectGenerator._flask_main(),
                    "requirements.txt": "flask==3.0.0\nrequests==2.31.0\n",
                    "README.md": "# Web App\n\nEjecutar: pip install -r requirements.txt && python main.py\n",
                }
            },
        }
        
        return structures.get(project_type, {}).get(language, {})
    
    @staticmethod
    def _cmake_minecraft() -> str:
        return """cmake_minimum_required(VERSION 3.10)
project(MinecraftClone)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# OpenGL
find_package(OpenGL REQUIRED)

# GLFW
find_package(glfw3 REQUIRED)

# GLEW
find_package(GLEW REQUIRED)

# STB Image
include_directories(${CMAKE_SOURCE_DIR}/lib)

add_executable(minecraft
    src/main.cpp
    src/world.cpp
    src/renderer.cpp
    src/player.cpp
)

target_link_libraries(minecraft
    ${OPENGL_LIBRARIES}
    glfw
    GLEW::GLEW
)

target_include_directories(minecraft PRIVATE
    ${OPENGL_INCLUDE_DIR}
)
"""
    
    @staticmethod
    def _main_cpp() -> str:
        return """#include <iostream>
#include <gl/glew.h>
#include <GLFW/glfw3.h>
#include "renderer.hpp"
#include "world.hpp"
#include "player.hpp"

const int WINDOW_WIDTH = 1280;
const int WINDOW_HEIGHT = 720;

int main() {
    // Inicializar GLFW
    if (!glfwInit()) {
        std::cerr << "Error al inicializar GLFW" << std::endl;
        return -1;
    }
    
    // Configurar ventana
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    
    GLFWwindow* window = glfwCreateWindow(WINDOW_WIDTH, WINDOW_HEIGHT, "Minecraft Clone", nullptr, nullptr);
    if (!window) {
        glfwTerminate();
        return -1;
    }
    
    glfwMakeContextCurrent(window);
    
    // Inicializar GLEW
    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) {
        std::cerr << "Error al inicializar GLEW" << std::endl;
        return -1;
    }
    
    // Configurar OpenGL
    glEnable(GL_DEPTH_TEST);
    glClearColor(0.5f, 0.7f, 1.0f, 1.0f);
    
    // Inicializar componentes
    Renderer renderer;
    World world;
    Player player;
    
    std::cout << "=== Minecraft Clone ===" << std::endl;
    std::cout << "Controles: WASD - Moverse, ESPACIO - Saltar, ESC - Salir" << std::endl;
    
    // Bucle principal
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        
        // Limpiar
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        
        // Actualizar lógica
        player.update(world);
        
        // Renderizar
        renderer.render(world, player);
        
        glfwSwapBuffers(window);
    }
    
    glfwDestroyWindow(window);
    glfwTerminate();
    
    return 0;
}
"""
    
    @staticmethod
    def _world_hpp() -> str:
        return """#ifndef WORLD_HPP
#define WORLD_HPP

#include <vector>
#include <array>

const int CHUNK_SIZE = 16;
const int WORLD_HEIGHT = 128;

enum BlockType {
    AIR = 0,
    GRASS,
    DIRT,
    STONE,
    WOOD,
    LEAVES,
    WATER,
    SAND
};

struct Block {
    BlockType type;
    bool visible;
};

struct Chunk {
    int x, z;
    std::array<std::array<std::array<Block, CHUNK_SIZE>, WORLD_HEIGHT>, CHUNK_SIZE> blocks;
    
    Chunk(int chunkX, int chunkZ);
    void generate();
    Block& getBlock(int x, int y, int z);
    void setBlock(int x, int y, int z, BlockType type);
};

class World {
private:
    std::map<std::pair<int, int>, Chunk> chunks;
    
public:
    World();
    Chunk& getChunk(int chunkX, int chunkZ);
    Block& getBlock(int x, int y, int z);
    void setBlock(int x, int y, int z, BlockType type);
    void generateChunk(int chunkX, int chunkZ);
};

#endif // WORLD_HPP
"""
    
    @staticmethod
    def _world_cpp() -> str:
        return """#include "world.hpp"
#include <cmath>
#include <random>

Chunk::Chunk(int chunkX, int chunkZ) : x(chunkX), z(chunkZ) {
    // Inicializar todos los bloques como aire
    for (int y = 0; y < WORLD_HEIGHT; y++) {
        for (int x = 0; x < CHUNK_SIZE; x++) {
            for (int z = 0; z < CHUNK_SIZE; z++) {
                blocks[y][x][z] = {AIR, true};
            }
        }
    }
}

void Chunk::generate() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> heightNoise(0, 1);
    
    for (int x = 0; x < CHUNK_SIZE; x++) {
        for (int z = 0; z < CHUNK_SIZE; z++) {
            // Generar altura del terreno
            int height = static_cast<int>(heightNoise(gen) * 20) + 10;
            
            for (int y = 0; y < WORLD_HEIGHT; y++) {
                BlockType type = AIR;
                
                if (y < height) {
                    if (y == height - 1) type = GRASS;
                    else if (y > height - 5) type = DIRT;
                    else type = STONE;
                } else if (y == 0) {
                    type = STONE;  // Bedrock
                }
                
                blocks[y][x][z] = {type, type != AIR};
            }
        }
    }
}

Block& Chunk::getBlock(int x, int y, int z) {
    return blocks[y][x][z];
}

void Chunk::setBlock(int x, int y, int z, BlockType type) {
    blocks[y][x][z] = {type, type != AIR};
}

World::World() {}

Chunk& World::getChunk(int chunkX, int chunkZ) {
    auto key = std::make_pair(chunkX, chunkZ);
    if (chunks.find(key) == chunks.end()) {
        generateChunk(chunkX, chunkZ);
    }
    return chunks[key];
}

Block& World::getBlock(int x, int y, int z) {
    int chunkX = x / CHUNK_SIZE;
    int chunkZ = z / CHUNK_SIZE;
    int localX = ((x % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE;
    int localZ = ((z % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE;
    
    return getChunk(chunkX, chunkZ).getBlock(localX, y, localZ);
}

void World::setBlock(int x, int y, int z, BlockType type) {
    int chunkX = x / CHUNK_SIZE;
    int chunkZ = z / CHUNK_SIZE;
    int localX = ((x % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE;
    int localZ = ((z % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE;
    
    getChunk(chunkX, chunkZ).setBlock(localX, y, localZ, type);
}

void World::generateChunk(int chunkX, int chunkZ) {
    Chunk chunk(chunkX, chunkZ);
    chunk.generate();
    chunks[std::make_pair(chunkX, chunkZ)] = chunk;
}
"""
    
    @staticmethod
    def _renderer_hpp() -> str:
        return """#ifndef RENDERER_HPP
#define RENDERER_HPP

#include <gl/glew.h>
#include <vector>
#include "world.hpp"
#include "player.hpp"

class Renderer {
private:
    GLuint VAO, VBO, EBO;
    GLuint shaderProgram;
    
    void compileShader(GLuint shader, const char* source);
    GLuint createShaderProgram();
    
public:
    Renderer();
    ~Renderer();
    
    void render(const World& world, const Player& player);
    void renderChunk(const Chunk& chunk);
};

#endif // RENDERER_HPP
"""
    
    @staticmethod
    def _renderer_cpp() -> str:
        return """#include "renderer.hpp"
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

const char* vertexShaderSource = R"(
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
)";

const char* fragmentShaderSource = R"(
#version 330 core
out vec4 FragColor;
in vec2 TexCoord;

uniform sampler2D texture1;

void main() {
    FragColor = texture(texture1, TexCoord);
}
)";

Renderer::Renderer() {
    // Crear programa de shaders
    shaderProgram = createShaderProgram();
    
    // Configurar VAO/VBO
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glGenBuffers(1, &EBO);
    
    glBindVertexArray(VAO);
    
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
    
    // Posiciones
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    
    // Texturas
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    
    std::cout << "Renderer inicializado" << std::endl;
}

Renderer::~Renderer() {
    glDeleteVertexArrays(1, &VAO);
    glDeleteBuffers(1, &VBO);
    glDeleteBuffers(1, &EBO);
    glDeleteProgram(shaderProgram);
}

GLuint Renderer::createShaderProgram() {
    GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
    compileShader(vertexShader, vertexShaderSource);
    
    GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    compileShader(fragmentShader, fragmentShaderSource);
    
    GLuint program = glCreateProgram();
    glAttachShader(program, vertexShader);
    glAttachShader(program, fragmentShader);
    glLinkProgram(program);
    
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
    
    return program;
}

void Renderer::compileShader(GLuint shader, const char* source) {
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    
    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(shader, 512, nullptr, infoLog);
        std::cerr << "Error compilando shader: " << infoLog << std::endl;
    }
}

void Renderer::render(const World& world, const Player& player) {
    glUseProgram(shaderProgram);
    
    // Configurar matrices
    glm::mat4 model = glm::mat4(1.0f);
    glm::mat4 view = player.getViewMatrix();
    glm::mat4 projection = glm::perspective(glm::radians(75.0f), 1280.0f/720.0f, 0.1f, 1000.0f);
    
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"), 1, GL_FALSE, glm::value_ptr(model));
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "view"), 1, GL_FALSE, glm::value_ptr(view));
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
    
    // Renderizar chunks visibles
    glBindVertexArray(VAO);
    // Aquí iría el renderizado real de los chunks
}

void Renderer::renderChunk(const Chunk& chunk) {
    // Implementar renderizado de chunk con face culling
}
"""
    
    @staticmethod
    def _player_hpp() -> str:
        return """#ifndef PLAYER_HPP
#define PLAYER_HPP

#include <glm/glm.hpp>
#include "world.hpp"

class Player {
private:
    glm::vec3 position;
    glm::vec3 velocity;
    glm::vec2 rotation;
    
    float speed;
    float jumpForce;
    bool onGround;
    
public:
    Player();
    
    void update(World& world);
    void move(float dx, float dz);
    void jump();
    
    glm::mat4 getViewMatrix() const;
    glm::vec3 getPosition() const { return position; }
};

#endif // PLAYER_HPP
"""
    
    @staticmethod
    def _player_cpp() -> str:
        return """#include "player.hpp"
#include <glm/gtc/matrix_transform.hpp>

const float GRAVITY = 9.8f;
const float PLAYER_HEIGHT = 1.8f;
const float PLAYER_WIDTH = 0.6f;

Player::Player() 
    : position(0.0f, 50.0f, 0.0f)
    , velocity(0.0f)
    , rotation(0.0f)
    , speed(5.0f)
    , jumpForce(8.0f)
    , onGround(false) {}

void Player::update(World& world) {
    // Aplicar gravedad
    if (!onGround) {
        velocity.y -= GRAVITY * 0.016f;
    }
    
    // Actualizar posición
    position += velocity * 0.016f;
    
    // Colisión simple con el suelo
    int blockX = static_cast<int>(position.x);
    int blockY = static_cast<int>(position.y - PLAYER_HEIGHT);
    int blockZ = static_cast<int>(position.z);
    
    Block& blockBelow = world.getBlock(blockX, blockY, blockZ);
    
    if (blockBelow.type != AIR && velocity.y < 0) {
        position.y = blockY + 1 + PLAYER_HEIGHT;
        velocity.y = 0;
        onGround = true;
    } else {
        onGround = false;
    }
    
    // Límite inferior del mundo
    if (position.y < 0) {
        position.y = 50;
        velocity.y = 0;
    }
}

void Player::move(float dx, float dz) {
    float sinRot = sin(rotation.x);
    float cosRot = cos(rotation.x);
    
    position.x += (dx * cosRot - dz * sinRot) * speed * 0.016f;
    position.z += (dx * sinRot + dz * cosRot) * speed * 0.016f;
}

void Player::jump() {
    if (onGround) {
        velocity.y = jumpForce;
        onGround = false;
    }
}

glm::mat4 Player::getViewMatrix() const {
    glm::vec3 front;
    front.x = cos(rotation.x) * cos(rotation.y);
    front.y = sin(rotation.y);
    front.z = sin(rotation.x) * cos(rotation.y);
    
    return glm::lookAt(position, position + front, glm::vec3(0, 1, 0));
}
"""
    
    @staticmethod
    def _readme_minecraft() -> str:
        return """# 🎮 Minecraft Clone en C++

Clon básico de Minecraft usando OpenGL, GLFW y GLEW.

## 📋 Requisitos

- CMake 3.10+
- OpenGL 3.3+
- GLFW3
- GLEW
- GLM

## 🔧 Instalación en Ubuntu/Debian

```bash
sudo apt-get install cmake libglfw3-dev libglew-dev libglm-dev
```

## 🚀 Compilar y Ejecutar

```bash
mkdir build && cd build
cmake ..
make
./minecraft
```

## 🎮 Controles

- **WASD** - Moverse
- **ESPACIO** - Saltar
- **Mouse** - Mirar alrededor (por implementar)
- **ESC** - Salir

## 📁 Estructura

```
src/
├── main.cpp       # Punto de entrada
├── world.hpp/cpp  # Generación de mundo
├── renderer.hpp/cpp  # Renderizado OpenGL
└── player.hpp/cpp # Lógica del jugador
```

## 🛠️ Próximas Características

- [ ] Generación de terreno con Perlin noise
- [ ] Sistema de chunks
- [ ] Colisiones completas
- [ ] Interfaz de usuario
- [ ] Sistema de crafteo
- [ ] Multijugador

## 📄 Licencia

MIT License
"""
    
    @staticmethod
    def _flask_main() -> str:
        return """from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "¡Bienvenido a la API!", "status": "running"})

@app.route('/api/hello')
def hello():
    return jsonify({"message": "¡Hola desde Flask!"})

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({"echo": data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""


class AIDeveloper:
    """Desarrollador de IA autónomo."""
    
    @staticmethod
    def create_project(name: str, project_type: str, language: str) -> str:
        """Crear proyecto completo desde cero."""
        try:
            project_dir = os.path.join(PROJECTS_DIR, name)
            os.makedirs(project_dir, exist_ok=True)
            
            # Obtener estructura
            structure = ProjectGenerator.create_project_structure(name, project_type, language)
            
            if not structure:
                return f"❌ Tipo de proyecto '{project_type}' no soportado para {language}"
            
            # Crear archivos
            created = []
            for filename, content in structure.items():
                filepath = os.path.join(project_dir, filename)
                os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                created.append(filename)
            
            return f"✅ Proyecto '{name}' creado en {project_dir}\n\n📁 Archivos:\n" + "\n".join(f"  • {f}" for f in created)
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def analyze_repository(repo_url: str) -> str:
        """Analizar repositorio de GitHub."""
        try:
            # Extraer owner/repo de la URL
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not match:
                return "❌ URL de GitHub inválida"
            
            owner, repo = match.groups()
            
            # Obtener información del repositorio
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            resp = requests.get(api_url, timeout=10)
            
            if resp.status_code != 200:
                return f"❌ Error: {resp.status_code}"
            
            data = resp.json()
            
            # Obtener lenguajes
            lang_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
            lang_resp = requests.get(lang_url, timeout=10)
            languages = lang_resp.json() if lang_resp.status_code == 200 else {}
            
            info = (
                f"📊 **Análisis de {owner}/{repo}**\n\n"
                f"📝 **Descripción:** {data.get('description', 'Sin descripción')}\n"
                f"⭐ **Stars:** {data.get('stargazers_count', 0)}\n"
                f"🍴 **Forks:** {data.get('forks_count', 0)}\n"
                f"📅 **Actualizado:** {data.get('updated_at', '')[:10]}\n"
                f"🌟 **Lenguaje principal:** {data.get('language', 'N/A')}\n"
                f"📚 **Lenguajes:**\n"
            )
            
            for lang, bytes_ in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                info += f"  • {lang}: {bytes_ / 1024:.1f} KB\n"
            
            return info
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def optimize_repository(repo_url: str, goal: str = "performance") -> str:
        """Analizar y sugerir optimizaciones para un repositorio."""
        try:
            # Primero obtener info básica
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not match:
                return "❌ URL de GitHub inválida"
            
            owner, repo = match.groups()
            
            # Obtener archivos principales
            contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            resp = requests.get(contents_url, timeout=10)
            
            if resp.status_code != 200:
                return f"❌ Error al obtener contenidos"
            
            files = resp.json()
            code_files = [f for f in files if f['type'] == 'file' and f['name'].endswith(('.py', '.cpp', '.rs', '.js', '.ts'))]
            
            analysis = f"🔍 **Análisis de optimización para {owner}/{repo}**\n\n"
            analysis += f"🎯 **Objetivo:** {goal}\n\n"
            analysis += f"📁 **Archivos principales encontrados:** {len(code_files)}\n\n"
            
            for f in code_files[:10]:
                lang = CodeAnalyzer.detect_language(f['name'])
                analysis += f"• {f['name']} ({lang or 'desconocido'})\n"
            
            analysis += "\n💡 **Recomendaciones generales:**\n"
            analysis += "1. Revisar algoritmos O(n²) o superiores\n"
            analysis += "2. Optimizar uso de memoria\n"
            analysis += "3. Considerar caching para operaciones costosas\n"
            analysis += "4. Usar profiling para identificar bottlenecks\n"
            
            return analysis
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def explain_codebase(code: str, language: str) -> str:
        """Explicar qué hace un código."""
        prompt = f"""Eres un experto programador. Explica claramente qué hace este código {language}:

```{language}
{code[:3000]}
```

Explica:
1. Propósito general
2. Funciones/métodos principales
3. Flujo de ejecución
4. Posibles mejoras"""

        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.5, "num_predict": 1500}
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=OLLAMA_TIMEOUT)
            return resp.json().get("response", "No se pudo analizar el código")
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def convert_language(code: str, from_lang: str, to_lang: str) -> str:
        """Convertir código de un lenguaje a otro."""
        prompt = f"""Convierte este código de {from_lang} a {to_lang}.
Mantén la misma funcionalidad y lógica.

Código original ({from_lang}):
```{from_lang}
{code[:2500]}
```

Devuelve SOLO el código convertido en {to_lang}, sin explicaciones."""

        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 2000}
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=OLLAMA_TIMEOUT)
            return resp.json().get("response", "No se pudo convertir el código")
        
        except Exception as e:
            return f"❌ Error: {str(e)}"


# Instancia global
ai_dev = AIDeveloper()


def test_module():
    """Probar el módulo."""
    print("🧪 Probando módulo AI Developer...")
    
    # Probar creación de proyecto
    result = ai_dev.create_project("test_minecraft", "minecraft_clone", "cpp")
    print(result)
    
    # Probar análisis
    print("\n" + "="*50 + "\n")
    
    analyzer = CodeAnalyzer()
    test_file = os.path.join(PROJECTS_DIR, "test_minecraft", "src", "main.cpp")
    if os.path.exists(test_file):
        metrics = analyzer.analyze_file(test_file, "cpp")
        print(f"Métricas: {metrics}")
        
        issues = analyzer.find_issues(test_file, "cpp")
        print(f"Issues: {issues}")


if __name__ == "__main__":
    test_module()
