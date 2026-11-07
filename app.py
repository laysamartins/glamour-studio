import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from database import conectar, inicializar_banco

app = Flask(__name__)
app.secret_key = "glamour_chave_secreta"

inicializar_banco()

@app.route("/")
def inicio():
    conexao = conectar()

    total_clientes = conexao.execute(
        "SELECT COUNT(*) FROM clientes"
    ).fetchone()[0]

    total_servicos = conexao.execute(
        "SELECT COUNT(*) FROM servicos"
    ).fetchone()[0]

    # vai contar quantos registros tem em cada tabela
    total_agendamentos = conexao.execute(
        "SELECT COUNT(*) FROM agendamentos"
    ).fetchone()[0]

    proximos = conexao.execute("""
        SELECT
            agendamentos.id,
            clientes.nome AS cliente,
            servicos.nome AS servico,
            agendamentos.data,
            agendamentos.horario
        FROM agendamentos
        JOIN clientes ON clientes.id = agendamentos.cliente_id
        JOIN servicos ON servicos.id = agendamentos.servico_id
        WHERE agendamentos.data >= date('now', 'localtime')
        ORDER BY agendamentos.data, agendamentos.horario
        LIMIT 5
    """).fetchall()

    conexao.close()

    # envia os dados para a página inicial
    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_servicos=total_servicos,
        total_agendamentos=total_agendamentos,
        proximos=proximos
    )
# vai exibir a lista e cadastros novos de clientes
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    conexao = conectar()

    if request.method == "POST":
        nome = request.form["nome"].strip()
        telefone = request.form["telefone"].strip()
        email = request.form.get("email", "").strip()

        # campos obrigatórios
        if not nome or not telefone:
            flash("Preencha o nome e o telefone.")
        else:
            conexao.execute("""
                INSERT INTO clientes (nome, telefone, email)
                VALUES (?, ?, ?)
            """, (nome, telefone, email))

            conexao.commit()
            flash("Cliente cadastrado com sucesso!")

        conexao.close()
        return redirect(url_for("clientes"))
    
    # consulta em ordem
    lista_clientes = conexao.execute(
        "SELECT * FROM clientes ORDER BY nome"
    ).fetchall()

    conexao.close()

    return render_template(
        "clientes.html",
        clientes=lista_clientes
    )

# exclui pelo id
@app.route("/clientes/excluir/<int:id>", methods=["POST"])
def excluir_cliente(id):
    conexao = conectar()

    try:
        conexao.execute(
            "DELETE FROM clientes WHERE id = ?", (id,)
        )
        conexao.commit()
        flash("Cliente excluído com sucesso!")
    except Exception:
        # se der erro aparece a mensagem e desfaz a operação
        conexao.rollback()
        flash("Não foi possível excluir. O cliente possui agendamentos.")

    conexao.close()

    return redirect(url_for("clientes"))

# cadastro e exibição dos serviços do salão
@app.route("/servicos", methods=["GET", "POST"])
def servicos():
    conexao = conectar()

    if request.method == "POST":
        nome = request.form["nome"].strip()

        try:
            # converte para numérico
            preco = float(request.form["preco"])
            duracao = int(request.form["duracao"])

            # responsável por não permitir espaço vazio, número negativo tempo menor que 0
            if not nome or preco < 0 or duracao <= 0:
                raise ValueError

            conexao.execute("""
                INSERT INTO servicos (nome, preco, duracao)
                VALUES (?, ?, ?)
            """, (nome, preco, duracao))

            conexao.commit()
            flash("Serviço cadastrado com sucesso!")

        except ValueError:
            flash("Verifique os dados do serviço.")

        conexao.close()
        return redirect(url_for("servicos"))

    lista_servicos = conexao.execute(
        "SELECT * FROM servicos ORDER BY nome"
    ).fetchall()

    conexao.close()

    return render_template(
        "servicos.html",
        servicos=lista_servicos
    )

# cadastro de horario e lista dos que já existem 
@app.route("/agendamentos", methods=["GET", "POST"])
def agendamentos():
    conexao = conectar()

    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        servico_id = request.form["servico_id"]
        data = request.form["data"]
        horario = request.form["horario"]

        try:
            # insere o agendamento com o cliente, serviço, data e horário.
            conexao.execute("""
                INSERT INTO agendamentos
                (cliente_id, servico_id, data, horario)
                VALUES (?, ?, ?, ?)
            """, (cliente_id, servico_id, data, horario))

            conexao.commit()
            flash("Agendamento realizado com sucesso!")

        except sqlite3.IntegrityError:
            # reverte a operação se tiver duplicidade ou dado inválido
            conexao.rollback()
            flash("Esse horário já está ocupado ou os dados são inválidos.")

        conexao.close()
        return redirect(url_for("agendamentos"))

    # busca de clientes e serviços para preencher os campos 
    lista_clientes = conexao.execute(
        "SELECT * FROM clientes ORDER BY nome"
    ).fetchall()

    lista_servicos = conexao.execute(
        "SELECT * FROM servicos ORDER BY nome"
    ).fetchall()

    # mostra nome do cliente e serviço juntando as tabelas 
    lista_agendamentos = conexao.execute("""
        SELECT
            agendamentos.id,
            clientes.nome AS cliente,
            servicos.nome AS servico,
            agendamentos.data,
            agendamentos.horario
        FROM agendamentos
        JOIN clientes ON clientes.id = agendamentos.cliente_id
        JOIN servicos ON servicos.id = agendamentos.servico_id
        ORDER BY agendamentos.data, agendamentos.horario
    """).fetchall()

    conexao.close()

    # vai enviar essas listas para a pagina de agendamentos
    return render_template(
        "agendamentos.html",
        clientes=lista_clientes,
        servicos=lista_servicos,
        agendamentos=lista_agendamentos
    )

# vai fazer a remoção do cliente pelo id
@app.route("/agendamentos/cancelar/<int:id>", methods=["POST"])
def cancelar_agendamento(id):
    conexao = conectar()

    conexao.execute(
        "DELETE FROM agendamentos WHERE id = ?", (id,)
    )

    conexao.commit()
    conexao.close()

    flash("Agendamento cancelado.")

    return redirect(url_for("agendamentos"))

# executa o servidor com inicio direto
if __name__ == "__main__":
    app.run(debug=True)