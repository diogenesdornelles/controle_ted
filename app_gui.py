"""
# My first app
Here's our first attempt at using data to create a table:
"""

from pathlib import Path

import streamlit as st
from pandas import DataFrame

from app_dataframe.statefull_dataframe_handler import statefull_dataframe_handler
from app_state.app_state import state

st.html("")


# Instruções renderizadas quando houve clique no btn dialog
@st.dialog("Instruções", width="large")
def show_instructions() -> None:
    """Mostra menu de instruções"""
    st.markdown(
        "<h2 style='color: #3498db;'>Forneça uma planilha Excel com extensão <code>.xlsx</code></h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='color: #2ecc71;'>A planilha deve conter 9 colunas com as seguintes informações:</h3>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <ul style='line-height: 1.6;'>
        <li><strong>Termo</strong></li>
        <li><strong>SIAFI</strong></li>
        <li><strong>Unidade Gestora Proponente</strong></li>
        <li><strong>Unidade Gestora Concedente</strong></li>
        <li><strong>Título / Objeto da despesa</strong></li>
        <li><strong>Situação Documento</strong></li>
        <li><strong>Coordenação</strong></li>
        <li><strong>Vigência inicial</strong> (dd/mm/aaaa)</li>
        <li><strong>Vigência fim</strong> (dd/mm/aaaa)</li>
    </ul>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div style='background-color: #f9f9f9; padding: 15px; border-left: 5px solid #e74c3c;'>
        <p>O sistema calcula automaticamente os 120 dias para prestação de contas e emite aviso 35 dias antes do fim da vigência.</p>
        <p>O sistema somente envia e-mail se houver uma planilha válida e houver a inicialização da rotina.</p>
        <p>É possível interromper a rotina a qualquer momento.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("Fechar"):
        st.rerun()


def always_run_components() -> None:
    """_summary_"""
    if st.button(
        ":material/integration_instructions: Ver instruções",
        help="Visualizar instruções",
        type="primary",
    ):
        show_instructions()

    # Estado da rotina sempre é renderizado
    if state.task_process["since"]:
        st.sidebar.info(
            f':material/sprint: Tarefa ativa desde {state.task_process["since"]}'
        )
    else:
        st.sidebar.info(":material/stop_circle: Tarefa inativa no momento")

    if Path("planilha.xlsx").exists():
        st.sidebar.warning(":material/description: Há planilha salva")
    else:
        st.sidebar.error(":material/block: Não Há planilha salva. Carregue uma!")


def handle_new() -> None:
    """_summary_"""
    file_uploaded = st.session_state["file_uploaded"]
    if file_uploaded is not None:
        if not state.file_uploaded:
            state.file_uploaded = file_uploaded

        else:
            if file_uploaded.file_id != state.file_uploaded:
                state.file_uploaded = file_uploaded
            else:
                state.df = False
                state.file_uploaded = None
    else:
        state.df = False
        state.file_uploaded = None

    if state.file_uploaded:
        df = statefull_dataframe_handler.get_df(state.file_uploaded)
        if isinstance(df, DataFrame):
            state.df = df
        else:
            st.toast(":material/error: Planilha não foi carregada!")


def handle_save() -> None:
    """_summary_"""
    if isinstance(state.df, DataFrame):
        if statefull_dataframe_handler.save_df(state.df):
            st.toast(":material/add: Planilha salva com sucesso!")
        else:
            st.toast(":material/error: Planilha não pôde ser salva!")
    else:
        st.toast(":material/error: Não há planilha previamente aberta!")


def handle_hide() -> None:
    """_summary_"""
    if isinstance(state.df, DataFrame):
        state.df = False
    else:
        st.toast(":material/error: Aparentemente, não há planilha para remover da tela")


def handle_load() -> None:
    """_summary_"""
    state.df = statefull_dataframe_handler.get_df()
    if isinstance(state.df, DataFrame):
        st.toast(":material/cached: Planilha encontrada e carregada")
    else:
        st.toast(
            ":material/error: Ops... algo deu errado com o carregamento. Talvez não haja planilha salva"
        )


def handle_delete() -> None:
    """Summary"""
    if statefull_dataframe_handler.delete_dataframe():
        st.toast(":material/delete: Planilha deletada")
        if state.kill_task():
            st.toast(":material/cancel: Rotina desativada")
        else:
            st.toast(":material/info: Não há rotina para desativar")
        handle_hide()
    else:
        st.toast(":material/error: Aparentemente, não há planilha salva")


def handle_start() -> None:
    """_summary_"""
    if state.start_task():
        st.toast(":material/start: Rotina iniciada")
    else:
        st.toast(
            ":material/error: Ops... algo deu errado com o carregamento. Talvez não haja planilha salva"
        )


def handle_pause() -> None:
    """_summary_"""
    if state.kill_task():
        st.toast(":material/cancel: Rotina desativada")
    else:
        st.toast(":material/error: Aparentemente, não há rotina para desativar")


if __name__ == "__main__":

    # Interface principal da aplicação
    st.title("Controle de TEDs")
    st.sidebar.title("Menu")

    if not state.is_logged:
        with st.form("Faça login"):
            username = st.text_input(
                "Username",
                placeholder="Usename",
                autocomplete="",
                help="Nome de usuário",
            )
            pwd = st.text_input(
                "Senha", placeholder="senha", type="password", autocomplete=None, help="senha"
            )
            btn_sbm = st.form_submit_button("Logar", type="primary")
            if btn_sbm:
                if not state.check_login(user=username, pwd=pwd):
                    st.toast("Username ou senha incorretos!")

    else:
        always_run_components()
        # handle_new()
        st.sidebar.divider()
        st.sidebar.write(":material/draft: Arquivo")
        if isinstance(state.df, DataFrame):
            LABEL = ":material/upload: Carregar arquivo Excel"
        else:
            LABEL = ":material/upload: Carregar novo arquivo Excel"
        st.sidebar.file_uploader(
            label=LABEL,
            type=["xlsx"],
            on_change=handle_new,
            key="file_uploaded",
        )

        st.sidebar.button(
            ":material/file_save: Salvar",
            use_container_width=True,
            on_click=handle_save,
            help="Clique para salvar a planilha. A planilha somente será salva se houve carregamento prévio.",
        )
        st.sidebar.button(
            ":material/delete: Deletar",
            use_container_width=True,
            help="Apague uma planilha salva. Isso causará a desativação da rotina",
            on_click=handle_delete,
        )
        st.sidebar.download_button(
            ":material/download: Baixar",
            data=(
                state.df.to_string().encode("utf-8")
                if isinstance(state.df, DataFrame)
                else DataFrame(statefull_dataframe_handler.columns)
                .to_string()
                .encode("utf-8")
            ),
            file_name="ted.xlsx",
            use_container_width=True,
        )

        st.sidebar.divider()
        st.sidebar.write(":material/data_table: Planilha")
        st.sidebar.button(
            ":material/file_open: Abrir",
            use_container_width=True,
            help="Carregar uma planilha salva",
            on_click=handle_load,
        )
        st.sidebar.button(
            ":material/close: Fechar",
            use_container_width=True,
            help="Remova a planilha da tela",
            on_click=handle_hide,
        )

        st.sidebar.divider()
        st.sidebar.write(":material/task_alt: Rotina")
        st.sidebar.button(
            ":material/start: Iniciar",
            use_container_width=True,
            help="Inicia uma rotina, desde que haja planilha salva",
            on_click=handle_start,
        )
        st.sidebar.button(
            ":material/cancel: Interromper",
            use_container_width=True,
            help="Pausar a rotina. Clique em inicial rotina para continuar",
            on_click=handle_pause,
        )
        # Exibe o DataFrame se ele existir
        if isinstance(state.df, DataFrame):
            st.dataframe(state.df, use_container_width=True)
        else:
            st.write("Nenhuma planilha carregada.")
