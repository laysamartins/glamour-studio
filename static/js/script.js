document.addEventListener("DOMContentLoaded", function () {

    // busca o campo de data do formulário
    const campoData = document.getElementById("data_agendamento");

    if (campoData) {
        const hoje = new Date();
        const ano = hoje.getFullYear();
        
        // formata para o padrão AAAA-MM-DD
        const mes = String(hoje.getMonth() + 1).padStart(2, "0");
        const dia = String(hoje.getDate()).padStart(2, "0");
    
        campoData.min = `${ano}-${mes}-${dia}`;
    }

});