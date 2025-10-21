/**
 * NeoCargo - Development Features Handler
 * Gerencia links e botões de funcionalidades em desenvolvimento
 */

;(function () {
  'use strict'

  /**
   * Exibe mensagem amigável para funcionalidades em desenvolvimento
   * @param {Event} event - Evento do click
   */
  function handleDevelopmentFeature(event) {
    event.preventDefault()
    const featureName =
      this.getAttribute('data-feature') || 'Esta funcionalidade'
    alert(
      `${featureName} está em desenvolvimento.\nEm breve estará disponível!`
    )
  }

  /**
   * Inicializa os event listeners
   */
  function init() {
    // Seleciona todos os elementos com data-development
    const developmentElements = document.querySelectorAll(
      '[data-development="true"]'
    )

    developmentElements.forEach(element => {
      element.addEventListener('click', handleDevelopmentFeature)
    })
  }

  // Inicializa quando o DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init)
  } else {
    init()
  }
})()
