#!/usr/bin/env python3
"""
J.A.R.V.I.S. - PROJECT GENERATOR
Generador de proyectos completos tipo Claude/Clawdbot
Crea proyectos completos desde cero con un solo comando
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
PROJECTS_DIR = os.path.join(WORKING_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)


class ProjectTemplate:
    """Plantilla de proyecto completo."""
    
    def __init__(self, name: str, project_type: str, language: str):
        self.name = name
        self.type = project_type
        self.language = language
        self.files = {}
        self.instructions = ""
    
    def add_file(self, path: str, content: str):
        self.files[path] = content
    
    def generate(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type,
            "language": self.language,
            "files": self.files,
            "file_count": len(self.files),
            "total_size": sum(len(c) for c in self.files.values()),
            "instructions": self.instructions
        }


class ProjectTemplates:
    """Colección de plantillas de proyectos."""
    
    @staticmethod
    def python_web_api(name: str) -> ProjectTemplate:
        """API Web en Python con FastAPI."""
        t = ProjectTemplate(name, "python_web_api", "python")
        
        t.add_file("README.md", f"""# {name}

API Web construida con FastAPI por J.A.R.V.I.S.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /` - Root
- `GET /api/health` - Health check
- `GET /api/items` - Listar items
- `POST /api/items` - Crear item
""")
        
        t.add_file("requirements.txt", """fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
python-dotenv>=1.0.0
""")
        
        t.add_file("main.py", '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="''' + name + '''",
    description="API generada por J.A.R.V.I.S.",
    version="1.0.0"
)

# Modelos
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    created_at: Optional[str] = None

# Base de datos en memoria
items_db = []

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a ''' + name + '''",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "items_count": len(items_db)
    }

@app.get("/api/items", response_model=List[Item])
async def list_items():
    """Listar todos los items"""
    return items_db

@app.get("/api/items/{item_id}")
async def get_item(item_id: int):
    """Obtener item por ID"""
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.post("/api/items", response_model=Item)
async def create_item(item: Item):
    """Crear nuevo item"""
    item.id = len(items_db) + 1
    item.created_at = datetime.now().isoformat()
    items_db.append(item.dict())
    return item

@app.put("/api/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """Actualizar item"""
    for i, existing in enumerate(items_db):
        if existing["id"] == item_id:
            items_db[i] = {**item.dict(), "id": item_id}
            return items_db[i]
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.delete("/api/items/{item_id}")
async def delete_item(item_id: int):
    """Eliminar item"""
    for i, existing in enumerate(items_db):
        if existing["id"] == item_id:
            return items_db.pop(i)
    raise HTTPException(status_code=404, detail="Item no encontrado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
        
        t.add_file("config.py", '''"""Configuración del proyecto"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "''' + name + '''"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

settings = Settings()
''')
        
        t.add_file(".env", '''# Configuración
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key-here
''')
        
        t.add_file(".gitignore", '''__pycache__/
*.pyc
.env
venv/
*.egg-info/
''')
        
        t.instructions = f"""
📦 Para ejecutar {name}:

1. Instalar dependencias:
   pip install -r requirements.txt

2. Configurar variables de entorno:
   cp .env.example .env
   # Editar .env con tus valores

3. Ejecutar:
   python main.py

4. Abrir en navegador:
   http://localhost:8000
   http://localhost:8000/docs (Swagger UI)
"""
        
        return t
    
    @staticmethod
    def python_cli(name: str) -> ProjectTemplate:
        """CLI en Python."""
        t = ProjectTemplate(name, "python_cli", "python")
        
        t.add_file("README.md", f"""# {name}

Herramienta de línea de comandos generada por J.A.R.V.I.S.

## Instalación

```bash
pip install -r requirements.txt
python cli.py --help
```
""")
        
        t.add_file("requirements.txt", """click>=8.1.0
rich>=13.0.0
""")
        
        t.add_file("cli.py", '''#!/usr/bin/env python3
"""CLI generada por J.A.R.V.I.S."""

import click
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()

@click.group()
@click.version_option("1.0.0")
def cli():
    """''' + name + ''' - CLI Tool"""
    pass

@cli.command()
def hello():
    """Saludar"""
    console.print("[bold green]¡Hola![/bold green] 👋")
    console.print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

@cli.command()
@click.option("--name", "-n", default="mundo", help="Nombre a saludar")
def greet(name):
    """Saludar a alguien"""
    console.print(f"[bold blue]¡Hola, {name}![/bold blue] 🌟")

@cli.command()
def status():
    """Ver estado del sistema"""
    table = Table(title="Estado del Sistema")
    table.add_column("Componente", style="cyan")
    table.add_column("Estado", style="green")
    table.add_row("CLI", "✅ Activo")
    table.add_row("Versión", "1.0.0")
    table.add_row("Fecha", datetime.now().strftime("%Y-%m-%d"))
    console.print(table)

@cli.command()
@click.argument("texto")
def reverse(texto):
    """Invertir texto"""
    console.print(f"[bold]Original:[/bold] {texto}")
    console.print(f"[bold]Invertido:[/bold] {texto[::-1]}")

if __name__ == "__main__":
    cli()
''')
        
        t.instructions = f"""
📦 Para usar {name}:

1. Instalar: pip install -r requirements.txt
2. Ver ayuda: python cli.py --help
3. Ejemplos:
   python cli.py hello
   python cli.py greet --name "Juan"
   python cli.py status
   python cli.py reverse "hola mundo"
"""
        
        return t
    
    @staticmethod
    def nodejs_express(name: str) -> ProjectTemplate:
        """API en Node.js con Express."""
        t = ProjectTemplate(name, "nodejs_express", "javascript")
        
        t.add_file("README.md", f"""# {name}

API REST con Express.js generada por J.A.R.V.I.S.

## Instalación

```bash
npm install
npm start
```
""")
        
        t.add_file("package.json", '''{
  "name": "''' + name.lower().replace(" ", "-") + '''",
  "version": "1.0.0",
  "description": "API generada por J.A.R.V.I.S.",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0"
  }
}
''')
        
        t.add_file("index.js", '''const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Base de datos en memoria
let items = [];

// Routes
app.get('/', (req, res) => {
  res.json({
    message: 'Bienvenido a ''' + name + '''',
    version: '1.0.0'
  });
});

app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    itemsCount: items.length
  });
});

app.get('/api/items', (req, res) => {
  res.json(items);
});

app.get('/api/items/:id', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({ error: 'Item no encontrado' });
  res.json(item);
});

app.post('/api/items', (req, res) => {
  const item = {
    id: items.length + 1,
    name: req.body.name,
    description: req.body.description,
    createdAt: new Date().toISOString()
  };
  items.push(item);
  res.status(201).json(item);
});

app.delete('/api/items/:id', (req, res) => {
  const index = items.findIndex(i => i.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'No encontrado' });
  items.splice(index, 1);
  res.json({ message: 'Item eliminado' });
});

app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
''')
        
        t.add_file(".env", "PORT=3000\n")
        
        t.instructions = f"""
📦 Para ejecutar {name}:

1. Instalar: npm install
2. Ejecutar: npm start
3. Abrir: http://localhost:3000
"""
        
        return t
    
    @staticmethod
    def react_app(name: str) -> ProjectTemplate:
        """App React básica."""
        t = ProjectTemplate(name, "react_app", "javascript")
        
        t.add_file("README.md", f"""# {name}

App React generada por J.A.R.V.I.S.

## Instalación

```bash
npm install
npm start
```
""")
        
        t.add_file("package.json", '''{
  "name": "''' + name.lower().replace(" ", "-") + '''",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
''')
        
        t.add_file("public/index.html", '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>''' + name + '''</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
''')
        
        t.add_file("src/index.js", '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
''')
        
        t.add_file("src/App.js", '''import React, { useState } from 'react';

function App() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  return (
    <div style={{ textAlign: 'center', padding: '40px', fontFamily: 'Arial' }}>
      <h1>''' + name + '''</h1>
      <p>App generada por J.A.R.V.I.S. 🤖</p>
      
      <div style={{ margin: '20px 0' }}>
        <h2>Contador: {count}</h2>
        <button onClick={() => setCount(count + 1)}>Incrementar</button>
        <button onClick={() => setCount(count - 1)} style={{ marginLeft: '10px' }}>Decrementar</button>
      </div>
      
      <div>
        <input
          type="text"
          placeholder="Escribe tu nombre"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ padding: '10px', fontSize: '16px' }}
        />
        {name && <h3>¡Hola, {name}! 👋</h3>}
      </div>
    </div>
  );
}

export default App;
''')
        
        t.instructions = f"""
📦 Para ejecutar {name}:

1. Instalar: npm install
2. Ejecutar: npm start
3. Abrir: http://localhost:3000
"""
        
        return t
    
    @staticmethod
    def minecraft_clone(name: str) -> ProjectTemplate:
        """Clon básico de Minecraft en C++."""
        t = ProjectTemplate(name, "minecraft_clone", "cpp")
        
        t.add_file("README.md", f"""# {name}

Clon de Minecraft en C++ con OpenGL generado por J.A.R.V.I.S.

## Requisitos

- CMake 3.10+
- OpenGL
- GLFW3
- GLEW
- GLM

## Compilar

```bash
mkdir build && cd build
cmake ..
make
./minecraft
```
""")
        
        t.add_file("CMakeLists.txt", '''cmake_minimum_required(VERSION 3.10)
project(MinecraftClone)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(GLEW REQUIRED)

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
''')
        
        t.add_file("src/main.cpp", '''#include <iostream>
#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include "world.hpp"
#include "renderer.hpp"
#include "player.hpp"

int main() {
    if (!glfwInit()) {
        std::cerr << "Error al inicializar GLFW" << std::endl;
        return -1;
    }
    
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    
    GLFWwindow* window = glfwCreateWindow(1280, 720, "''' + name + '''", nullptr, nullptr);
    if (!window) {
        glfwTerminate();
        return -1;
    }
    
    glfwMakeContextCurrent(window);
    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) {
        std::cerr << "Error al inicializar GLEW" << std::endl;
        return -1;
    }
    
    glEnable(GL_DEPTH_TEST);
    glClearColor(0.5f, 0.7f, 1.0f, 1.0f);
    
    Renderer renderer;
    World world;
    Player player;
    
    std::cout << "=== ''' + name + ''' ===" << std::endl;
    std::cout << "Controles: WASD - Moverse, ESPACIO - Saltar" << std::endl;
    
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        player.update(world);
        renderer.render(world, player);
        glfwSwapBuffers(window);
    }
    
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
''')
        
        t.add_file("src/world.hpp", '''#ifndef WORLD_HPP
#define WORLD_HPP

#include <vector>
#include <map>

const int CHUNK_SIZE = 16;
const int WORLD_HEIGHT = 64;

enum BlockType { AIR = 0, GRASS, DIRT, STONE, WOOD, LEAVES };

struct Block { BlockType type; bool visible; };

class World {
public:
    World();
    BlockType getBlock(int x, int y, int z);
    void setBlock(int x, int y, int z, BlockType type);
    void generateChunk(int cx, int cz);
};

#endif
''')
        
        t.add_file("src/world.cpp", '''#include "world.hpp"
#include <cmath>
#include <random>

World::World() {}

BlockType World::getBlock(int x, int y, int z) {
    if (y < 0 || y >= WORLD_HEIGHT) return AIR;
    int height = 10 + static_cast<int>(std::sin(x * 0.1) * 3 + std::cos(z * 0.1) * 3);
    if (y == height - 1) return GRASS;
    if (y < height - 1 && y > height - 5) return DIRT;
    if (y <= height - 5) return STONE;
    return AIR;
}

void World::setBlock(int x, int y, int z, BlockType type) {}
void World::generateChunk(int cx, int cz) {}
''')
        
        t.add_file("src/renderer.hpp", '''#ifndef RENDERER_HPP
#define RENDERER_HPP

#include <GL/glew.h>
#include "world.hpp"
#include "player.hpp"

class Renderer {
public:
    Renderer();
    void render(const World& world, const Player& player);
private:
    GLuint shaderProgram;
    GLuint VAO, VBO;
};

#endif
''')
        
        t.add_file("src/renderer.cpp", '''#include "renderer.hpp"

Renderer::Renderer() {
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glBindVertexArray(VAO);
}

void Renderer::render(const World& world, const Player& player) {
    glUseProgram(shaderProgram);
    // Renderizado de chunks aquí
}
''')
        
        t.add_file("src/player.hpp", '''#ifndef PLAYER_HPP
#define PLAYER_HPP

#include <glm/glm.hpp>
#include "world.hpp"

class Player {
public:
    Player();
    void update(World& world);
    glm::mat4 getViewMatrix() const;
private:
    glm::vec3 position;
    glm::vec3 velocity;
    glm::vec2 rotation;
    bool onGround;
};

#endif
''')
        
        t.add_file("src/player.cpp", '''#include "player.hpp"
#include <glm/gtc/matrix_transform.hpp>

Player::Player() : position(0, 30, 0), velocity(0), onGround(false) {}

void Player::update(World& world) {
    velocity.y -= 9.8f * 0.016f;
    position += velocity * 0.016f;
    
    int blockY = static_cast<int>(position.y - 1.8f);
    if (world.getBlock(static_cast<int>(position.x), blockY, static_cast<int>(position.z)) != AIR) {
        position.y = blockY + 1 + 1.8f;
        velocity.y = 0;
        onGround = true;
    }
}

glm::mat4 Player::getViewMatrix() const {
    return glm::mat4(1.0f);
}
''')
        
        t.instructions = f"""
📦 Para compilar {name}:

1. Instalar dependencias:
   sudo apt install cmake libglfw3-dev libglew-dev libglm-dev

2. Compilar:
   mkdir build && cd build
   cmake ..
   make

3. Ejecutar:
   ./minecraft
"""
        
        return t
    
    @staticmethod
    def get_all_templates() -> Dict[str, str]:
        """Obtener todas las plantillas disponibles."""
        return {
            "python_api": "API Web en Python con FastAPI",
            "python_cli": "Herramienta CLI en Python",
            "nodejs_api": "API REST en Node.js con Express",
            "react_app": "App React básica",
            "minecraft_clone": "Clon de Minecraft en C++"
        }


class ProjectGenerator:
    """Generador de proyectos completos."""
    
    def __init__(self):
        self.templates = ProjectTemplates()
        self.created_projects = []
    
    def create_project(self, description: str) -> Dict:
        """Crear proyecto basado en descripción."""
        desc_lower = description.lower()
        
        # Detectar tipo de proyecto
        project_type = self._detect_project_type(desc_lower)
        name = self._extract_project_name(description, project_type)
        language = self._detect_language(desc_lower)
        
        # Generar proyecto
        template = self._get_template(project_type, name)
        project = template.generate()
        
        # Crear archivos en disco
        project_dir = os.path.join(PROJECTS_DIR, name)
        os.makedirs(project_dir, exist_ok=True)
        
        created_files = []
        for filepath, content in project["files"].items():
            full_path = os.path.join(project_dir, filepath)
            os.makedirs(os.path.dirname(full_path) or project_dir, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(filepath)
        
        project["directory"] = project_dir
        project["created_files"] = created_files
        project["success"] = True
        
        self.created_projects.append(project)
        
        return project
    
    def _detect_project_type(self, desc_lower: str) -> str:
        """Detectar tipo de proyecto."""
        if any(x in desc_lower for x in ["minecraft", "voxel", "juego 3d", "clone minecraft"]):
            return "minecraft_clone"
        if any(x in desc_lower for x in ["react", "frontend", "web app", "aplicación web"]):
            return "react_app"
        if any(x in desc_lower for x in ["node", "express", "javascript", "js"]):
            return "nodejs_api"
        if any(x in desc_lower for x in ["cli", "comandos", "terminal", "línea de comandos"]):
            return "python_cli"
        if any(x in desc_lower for x in ["api", "fastapi", "backend", "servidor", "web"]):
            return "python_api"
        
        # Default
        return "python_api"
    
    def _extract_project_name(self, description: str, project_type: str) -> str:
        """Extraer nombre del proyecto."""
        import re
        
        # Buscar nombre explícito
        match = re.search(r'(?:llamado|nombre|named)\s+(\w[\w\s-]+?)(?:\s+con|\s+en|\s+de|$)', description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Generar nombre basado en tipo
        type_names = {
            "python_api": "mi_api",
            "python_cli": "mi_cli",
            "nodejs_api": "mi_api_node",
            "react_app": "mi_app_react",
            "minecraft_clone": "mi_minecraft"
        }
        
        return type_names.get(project_type, "mi_proyecto")
    
    def _detect_language(self, desc_lower: str) -> str:
        """Detectar lenguaje preferido."""
        if "python" in desc_lower:
            return "python"
        if "javascript" in desc_lower or "node" in desc_lower:
            return "javascript"
        if "react" in desc_lower:
            return "javascript"
        if "c++" in desc_lower or "cpp" in desc_lower:
            return "cpp"
        return "python"
    
    def _get_template(self, project_type: str, name: str) -> ProjectTemplate:
        """Obtener plantilla apropiada."""
        templates = {
            "python_api": self.templates.python_web_api,
            "python_cli": self.templates.python_cli,
            "nodejs_api": self.templates.nodejs_express,
            "react_app": self.templates.react_app,
            "minecraft_clone": self.templates.minecraft_clone
        }
        
        generator = templates.get(project_type, self.templates.python_web_api)
        return generator(name)
    
    def list_templates(self) -> str:
        """Listar plantillas disponibles."""
        templates = ProjectTemplates.get_all_templates()
        
        result = "📦 **Plantillas disponibles:**\n\n"
        for key, desc in templates.items():
            result += f"• `{key}` - {desc}\n"
        
        result += "\n**Ejemplos:**\n"
        result += "• 'Crea una API web llamada mi_api'\n"
        result += "• 'Crea un clon de Minecraft'\n"
        result += "• 'Crea una app React'\n"
        result += "• 'Crea una CLI en Python'\n"
        
        return result
    
    def get_project_summary(self) -> str:
        """Resumen de proyectos creados."""
        if not self.created_projects:
            return "📁 No hay proyectos creados aún."
        
        result = f"📁 **Proyectos creados ({len(self.created_projects)}):**\n\n"
        for p in self.created_projects:
            result += f"📦 **{p['name']}** ({p['type']})\n"
            result += f"   📄 {p['file_count']} archivos | 💾 {p['total_size']/1024:.1f} KB\n"
            result += f"   📁 {p['directory']}\n\n"
        
        return result


# Instancia global
project_generator = ProjectGenerator()


def test_generator():
    """Probar generador."""
    gen = ProjectGenerator()
    
    print("🏗️ Probando generador de proyectos...\n")
    
    # Crear proyecto
    project = gen.create_project("Crea una API web llamada mi_api_test")
    
    print(f"✅ Proyecto creado: {project['name']}")
    print(f"📄 Archivos: {project['file_count']}")
    print(f"📁 Directorio: {project['directory']}")
    print(f"\n📋 Archivos creados:")
    for f in project['created_files']:
        print(f"  • {f}")
    
    print(f"\n{project['instructions']}")
    
    print("\n✅ Generador probado")


if __name__ == "__main__":
    test_generator()
