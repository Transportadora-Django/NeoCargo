/**
 * NeoCargo - Gestão de Usuários
 * Gerencia funcionalidades da página de gestão de usuários
 */

document.addEventListener('DOMContentLoaded', function () {
  /**
   * Exibe mensagem para funcionalidades em desenvolvimento
   * @param {string} feature - Nome da funcionalidade
   */
  function showDevelopmentMessage(feature) {
    alert(
      `Funcionalidade "${feature}" em desenvolvimento.\nEm breve estará disponível!`
    )
  }

  // Adiciona event listeners para botões de ver veículos
  const verVeiculosButtons = document.querySelectorAll(
    '[data-action="ver-veiculos"]'
  )
  verVeiculosButtons.forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault()
      showDevelopmentMessage('Ver Veículos')
    })
  })
})
