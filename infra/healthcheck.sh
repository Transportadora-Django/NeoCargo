#!/bin/sh

# Health check script para produção
# Usado para verificar se a aplicação está rodando corretamente

echo "🔍 Verificando saúde da aplicação..."

# Verificar se o processo do Gunicorn está rodando
if pgrep -f "gunicorn" > /dev/null; then
    echo "✅ Gunicorn está rodando"
else
    echo "❌ Gunicorn não encontrado"
    exit 1
fi

# Verificar se a porta está sendo escutada
PORT=${PORT:-8000}
if netstat -tln | grep ":$PORT " > /dev/null; then
    echo "✅ Porta $PORT está sendo escutada"
else
    echo "❌ Porta $PORT não está sendo escutada"
    exit 1
fi

echo "✅ Aplicação está saudável"
exit 0