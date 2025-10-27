/**
 * NeoCargo - Filtro Dinâmico de Destinos
 * Filtra cidades de destino baseado na origem selecionada
 */

document.addEventListener('DOMContentLoaded', function () {
  const origemSelect = document.getElementById('id_cidade_origem')
  const destinoSelect = document.getElementById('id_cidade_destino')

  if (!origemSelect || !destinoSelect) {
    // eslint-disable-next-line no-console
    console.error('Selects de cidade não encontrados')
    return
  }

  // Guardar todas as opções de destino originais
  const todasOpcoesDestino = Array.from(destinoSelect.options).map(opt => ({
    value: opt.value,
    text: opt.text,
  }))

  // Função para filtrar destinos baseado na origem
  function filtrarDestinos() {
    const origemSelecionada = origemSelect.value

    // Limpar destino atual
    destinoSelect.innerHTML = '<option value="">Selecione uma cidade</option>'

    if (!origemSelecionada) {
      // Se não há origem, mostrar todas
      todasOpcoesDestino.forEach(opt => {
        if (opt.value) {
          const option = new Option(opt.text, opt.value)
          destinoSelect.add(option)
        }
      })
      return
    }

    // Fazer requisição para buscar destinos disponíveis
    fetch(
      `/pedidos/api/destinos-disponiveis/?origem=${encodeURIComponent(origemSelecionada)}`
    )
      .then(response => response.json())
      .then(data => {
        if (data.destinos && data.destinos.length > 0) {
          data.destinos.forEach(destino => {
            const option = new Option(destino, destino)
            destinoSelect.add(option)
          })
        } else {
          const option = new Option(
            'Nenhuma rota disponível para esta origem',
            ''
          )
          option.disabled = true
          destinoSelect.add(option)
        }
      })
      .catch(error => {
        // eslint-disable-next-line no-console
        console.error('Erro ao buscar destinos:', error)
        // Em caso de erro, mostrar todas as opções exceto a origem
        todasOpcoesDestino.forEach(opt => {
          if (opt.value && opt.value !== origemSelecionada) {
            const option = new Option(opt.text, opt.value)
            destinoSelect.add(option)
          }
        })
      })
  }

  // Adicionar evento de mudança na origem
  origemSelect.addEventListener('change', filtrarDestinos)

  // Filtrar na carga inicial se já houver uma origem selecionada
  if (origemSelect.value) {
    filtrarDestinos()
  }
})
