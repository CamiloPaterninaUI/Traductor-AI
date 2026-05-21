# 1. Inicializa git en la carpeta del proyecto
git init

# 2. Crea el .gitignore
echo "__pycache__/
*.pyc
.env
venv/
.venv/" > .gitignore

# 3. Agrega todos los archivos
git add .

# 4. Primer commit
git commit -m "feat: initial commit - Traductor-AI con Ollama + Qwen 2.5"

# 5. Conecta con tu repositorio de GitHub
git branch -M main
git remote add origin https://github.com/CamiloPaterninaUI/Traductor-AI.git

# 6. Sube todo
git push -u origin main
