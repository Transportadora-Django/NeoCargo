/**
 * NeoCargo - Mapa de Rotas
 * Gerencia a exibição do mapa interativo com Leaflet.js
 */

;(function () {
  'use strict'

  /**
   * Configurações do mapa
   */
  const CONFIG = {
    CENTER: [-14.235, -51.9253], // Centro do Brasil
    ZOOM: 4,
    MAX_ZOOM: 18,
    TILE_URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    TILE_ATTRIBUTION: '© OpenStreetMap contributors',
  }

  /**
   * Estilos dos marcadores e linhas
   */
  const STYLES = {
    cidade: {
      radius: 8,
      fillColor: '#06b6d4',
      color: '#fff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8,
    },
    rota: {
      color: '#10b981',
      weight: 3,
      opacity: 0.7,
    },
  }

  /**
   * Inicializa o mapa
   * @param {Array} cidades - Lista de cidades
   * @param {Array} rotas - Lista de rotas
   */
  function initMap(cidades, rotas) {
    // Criar mapa
    const map = L.map('map').setView(CONFIG.CENTER, CONFIG.ZOOM)

    // Adicionar camada de tiles
    L.tileLayer(CONFIG.TILE_URL, {
      attribution: CONFIG.TILE_ATTRIBUTION,
      maxZoom: CONFIG.MAX_ZOOM,
    }).addTo(map)

    // Adicionar marcadores de cidades
    addCityMarkers(map, cidades)

    // Adicionar linhas de rotas
    addRouteLines(map, rotas)

    return map
  }

  /**
   * Adiciona marcadores para as cidades
   * @param {L.Map} map - Instância do mapa
   * @param {Array} cidades - Lista de cidades
   */
  function addCityMarkers(map, cidades) {
    cidades.forEach(cidade => {
      const marker = L.circleMarker([cidade.lat, cidade.lng], STYLES.cidade).addTo(
        map
      )

      // Popup com informações da cidade
      const popupContent = createCityPopup(cidade)
      marker.bindPopup(popupContent)
    })
  }

  /**
   * Cria conteúdo do popup para cidade
   * @param {Object} cidade - Dados da cidade
   * @returns {string} HTML do popup
   */
  function createCityPopup(cidade) {
    return `
      <div style="text-align: center; min-width: 150px;">
        <strong style="font-size: 1.1rem; color: #1d3557;">
          ${cidade.nome_completo}
        </strong>
      </div>
    `
  }

  /**
   * Adiciona linhas para as rotas
   * @param {L.Map} map - Instância do mapa
   * @param {Array} rotas - Lista de rotas
   */
  function addRouteLines(map, rotas) {
    rotas.forEach(rota => {
      const latlngs = [
        [rota.origem.lat, rota.origem.lng],
        [rota.destino.lat, rota.destino.lng],
      ]

      const polyline = L.polyline(latlngs, STYLES.rota).addTo(map)

      // Popup com informações da rota
      const popupContent = createRoutePopup(rota)
      polyline.bindPopup(popupContent)
    })
  }

  /**
   * Cria conteúdo do popup para rota
   * @param {Object} rota - Dados da rota
   * @returns {string} HTML do popup
   */
  function createRoutePopup(rota) {
    let content = `
      <div style="min-width: 220px;">
        <div style="text-align: center; margin-bottom: 0.75rem;">
          <strong style="color: #1d3557;">${rota.origem.nome}</strong>
          <i class="fas fa-arrow-right mx-2" style="color: #06b6d4;"></i>
          <strong style="color: #1d3557;">${rota.destino.nome}</strong>
        </div>
        <div style="border-top: 1px solid #e2e8f0; padding-top: 0.75rem;">
          <div style="margin-bottom: 0.5rem;">
            <i class="fas fa-road" style="color: #06b6d4; width: 20px;"></i>
            <strong>Distância:</strong> ${rota.distancia} km
          </div>
    `

    if (rota.tempo) {
      const dias = (rota.tempo / 24).toFixed(1)
      content += `
        <div>
          <i class="fas fa-clock" style="color: #06b6d4; width: 20px;"></i>
          <strong>Tempo:</strong> ${rota.tempo.toFixed(1)}h (~${dias} dias)
        </div>
      `
    }

    content += `
        </div>
      </div>
    `

    return content
  }

  /**
   * Inicialização quando o DOM estiver pronto
   */
  function init() {
    // Verificar se existe elemento do mapa
    const mapElement = document.getElementById('map')
    if (!mapElement) {
      return
    }

    // Obter dados das cidades e rotas (injetados pelo template)
    const cidadesData = window.NEOCARGO_CIDADES || []
    const rotasData = window.NEOCARGO_ROTAS || []

    // Verificar se há dados
    if (cidadesData.length === 0) {
      mapElement.innerHTML = `
        <div class="map-loading">
          <div class="text-center">
            <i class="fas fa-map-marked-alt mb-3"></i>
            <p>Nenhuma cidade cadastrada ainda.</p>
          </div>
        </div>
      `
      return
    }

    // Inicializar mapa
    try {
      initMap(cidadesData, rotasData)
    } catch (error) {
      console.error('Erro ao inicializar mapa:', error)
      mapElement.innerHTML = `
        <div class="map-loading">
          <div class="text-center text-danger">
            <i class="fas fa-exclamation-triangle mb-3"></i>
            <p>Erro ao carregar o mapa. Por favor, recarregue a página.</p>
          </div>
        </div>
      `
    }
  }

  // Inicializar quando o DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init)
  } else {
    init()
  }
})()
