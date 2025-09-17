#!/bin/sh

# Script para validar arquivos estáticos antes do deploy
# Verifica se todos os arquivos referenciados nos templates existem

echo "🔍 Validando arquivos estáticos..."

# Função para verificar se arquivo existe
check_static_file() {
    local file_path="$1"
    local full_path="/app/ui/static/$file_path"
    
    if [ -f "$full_path" ]; then
        echo "✅ $file_path"
        return 0
    else
        echo "❌ $file_path (AUSENTE)"
        return 1
    fi
}

# Lista de arquivos críticos para verificar
CRITICAL_FILES="
assets/Logo-NeoCargo-White.svg
assets/Logo-NeoCargo.svg
css/style.css
css/alerts.css
js/app.js
"

# Verificar cada arquivo
missing_files=0
for file in $CRITICAL_FILES; do
    if ! check_static_file "$file"; then
        missing_files=$((missing_files + 1))
    fi
done

# Resultado
if [ $missing_files -eq 0 ]; then
    echo "✅ Todos os arquivos estáticos estão presentes!"
    exit 0
else
    echo "❌ $missing_files arquivo(s) ausente(s). Verifique antes do deploy!"
    exit 1
fi