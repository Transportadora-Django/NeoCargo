/**
 * NeoCargo - Solicitar Mudança de Perfil
 * Gerencia a exibição dinâmica de campos do formulário
 */

document.addEventListener('DOMContentLoaded', function () {
  const roleSelect = document.getElementById('id_role_solicitada')
  const dadosPessoais = document.getElementById('dados-pessoais')

  // Aplicar máscaras usando jQuery Mask Plugin
  if (typeof $ !== 'undefined' && $.fn.mask) {
    $('#id_telefone').mask('(00) 00000-0000')
    $('#id_cpf').mask('000.000.000-00')
  }

  /**
   * Alterna a visibilidade das seções baseado na role selecionada
   */
  function toggleSections() {
    const selectedRole = roleSelect.value

    // Mostra dados pessoais quando qualquer role for selecionado
    if (selectedRole) {
      dadosPessoais.style.display = 'block'
    } else {
      dadosPessoais.style.display = 'none'
    }
  }

  // Event listener para mudanças no select
  roleSelect.addEventListener('change', toggleSections)

  // Inicializar estado correto ao carregar a página
  toggleSections()
})
