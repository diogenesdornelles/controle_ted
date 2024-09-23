"""
# My first app streamlit
"""

from multiprocessing import Process
from pathlib import Path

import pandas as pd
from pandas import DataFrame

import streamlit as st
from app_dataframe.statefull_dataframe_handler import statefull_dataframe_handler
from app_state.app_state import state
from settings import settings
from utils.return_today_str import return_today_str


def set_chart() -> None:
    """
    Plots a scatter chart using dates from the uploaded spreadsheet.

    This function processes the relevant columns in the DataFrame, filters data
    based on today's date, sorts the DataFrame by specified columns, and then
    plots a scatter chart. It ensures that only relevant data (from today onward)
    is displayed in the chart.

    Steps:
    - Extracts the columns to work with (starting from the third-to-last column).
    - Converts the date column to the proper format for comparison.
    - Filters out rows with dates earlier than today.
    - Sorts the data by specified columns.
    - Displays the scatter chart using Streamlit.

    Args:
        None
    Returns:
        None
    """
    if isinstance(state.df, DataFrame):
        st.divider()
        st.subheader("Gráfico", divider=True)
        initial_data_column = -3
        df = pd.DataFrame()
        df["Termo"] = state.df.index.to_series(name="Termo")
        for column in statefull_dataframe_handler.columns[initial_data_column:]:
            df[column] = state.df[column]

        df.reset_index(inplace=True, drop=True)
        df.set_index("Termo", inplace=True)
        # Plot the line chart with the proper structure
        df[statefull_dataframe_handler.columns[initial_data_column]] = pd.to_datetime(
            df[statefull_dataframe_handler.columns[initial_data_column]],
            format="%d/%m/%Y",
        )
        df = df[
            df[statefull_dataframe_handler.columns[initial_data_column]]
            >= pd.to_datetime(return_today_str(), format="%d/%m/%Y")
        ]
        df[statefull_dataframe_handler.columns[initial_data_column]] = df[
            statefull_dataframe_handler.columns[initial_data_column]
        ].dt.strftime("%d/%m/%Y")
        order = [
            statefull_dataframe_handler.columns[-2],
            statefull_dataframe_handler.columns[-3],
            statefull_dataframe_handler.columns[-1],
        ]
        df.sort_values(
            by=order,
            inplace=True,
        )
        st.scatter_chart(
            df,
            y=order,  # Use the column values for the y-axis
            x_label="Termo",
            y_label="Datas",
            use_container_width=True,
        )


def dispatch(**kwargs):
    match kwargs["func"]:
        case "save":
            if not isinstance(state.df, DataFrame):
                st.toast(":material/error: Não há planilha previamente aberta!")
            else:
                confirm_pwd(kwargs["func"])
        case "delete":
            if not Path("planilha.xlsx").exists():
                st.toast(":material/error: Aparentemente, não há planilha para remover")
            else:
                confirm_pwd(kwargs["func"])
        case "start":
            if not Path("planilha.xlsx").exists() or isinstance(
                state.task_process["process"], Process
            ):
                st.toast(
                    ":material/error: Aparentemente, não há planilha para iniciar rotina ou a rotina já está iniciada"
                )
            else:
                confirm_pwd(kwargs["func"])
        case "pause":
            if not isinstance(state.task_process["process"], Process):
                st.toast(
                    ":material/error: Aparentemente, não há rotina para interromper"
                )
            else:
                confirm_pwd(kwargs["func"])
        case "new":
            handle_new()
        case "hide":
            handle_hide()
        case "load":
            handle_load()
        case "logout":
            handle_logout()


@st.dialog("Confirmação", width="large")
def confirm_pwd(func: str) -> None:
    """
    Displays a password confirmation dialog to verify critical actions.

    This function displays a dialog with a password input field. If the password is correct,
    it will trigger a specific function (save, delete, start, pause) based on the argument passed.

    Args:
        kwargs["func"] (str): The name of the action to execute after password verification
                              (e.g., 'save', 'delete', 'start', 'pause').

    Returns:
        None
    """
    st.write("Confirme sua senha")
    with st.form("Senha", clear_on_submit=True):
        pwd = st.text_input(
            "Senha",
            placeholder="senha",
            type="password",
            autocomplete=None,
            help="senha",
        )
        btn = st.form_submit_button("Verificar", type="primary")
        if btn and pwd and pwd == settings.user_pwd:
            match func:
                case "save":
                    handle_save()
                case "delete":
                    handle_delete()
                case "start":
                    handle_start()
                case "pause":
                    handle_pause()
            st.rerun()
    if st.button("Fechar"):
        st.rerun()


# Instruções renderizadas quando houve clique no btn dialog
@st.dialog("Instruções", width="large")
def show_instructions() -> None:
    """
    Displays a detailed instruction menu for uploading a valid Excel spreadsheet.

    This function provides the user with the necessary instructions, including the required
    format of the Excel file and columns. It uses HTML styling for enhanced visual presentation.

    Returns:
        None
    """
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
        "<h3 style='color: #2ecc71;'>Não inclua linhas de cabeçalho ou de rodapé. O sistema faz isso automaticamente.</h3>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div style='background-color: #f9f9f9; padding: 15px; border-left: 5px solid #e74c3c;'>
        <p>O sistema calcula automaticamente 120 dias para prestação de contas, após a vigência fim.</p>
        <p>O sistema calcula automaticamente de aviso de 35 dias, antes da vigência fim.</p>
        <p>O sistema somente envia e-mail se houver uma planilha válida devidamente salva e houver a inicialização da rotina no menu lateral.</p>
        <p>Não faça anotações às margens, lateral ou inferior da planilha.</p>
        <p>É possível interromper a rotina a qualquer momento.</p>
        <p>Por motivos de segurança, o aplicativo funciona com um tempo de sessão definido, ajustável no menu lateral, que pode variar entre 30 segundos e 10 minutos. A cada interação o tempo de sessão é restaurado.</p>
        <p>Linhas em que não há informações data serão excluídas</p>
        <p>Para coluna 'vigência início' sem data, será inserida a data de 01/01/1970</p>
        <p>Exemplo de planilha <a href="https://docs.google.com/spreadsheets/d/1taOxp_T8rBkl7Ge9G7WvriFNjsmyncrTzrDXhHoXm7g/edit?usp=sharing">AQUI</a></p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("Fechar"):
        st.rerun()


@st.fragment(run_every=7)
def timeout_counter():
    """
    Manages the countdown for the session timeout.

    This function reduces the user's session timeout and displays a progress bar.
    Once the timeout reaches zero, the user is automatically logged out.

    Returns:
        None
    """
    state.timeout -= 1
    if state.timeout > 0:
        st.progress(
            1 - (state.timeout / state.max_timeout), text="Tempo restante de sessão..."
        )
    else:
        state.is_logged = False
        st.rerun()


def always_run_components() -> None:
    """
    Renders persistent components on the sidebar.

    This function is responsible for showing user information, task status, and general
    application states that should always be visible in the sidebar. It also includes
    the ability to show instructions and manage task states.

    Returns:
        None
    """

    st.success(f"Bem-vindo(a): {state.username}")
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
    """
    Handles the process of loading a new file into the application.

    If a new file is uploaded, it updates the application state to reflect the new file.
    If no file is provided, it resets the state accordingly.

    Returns:
        None
    """
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
    """Saves the dataframa stored in state"""
    if statefull_dataframe_handler.save_df(state.df):
        st.toast(":material/add: Planilha salva com sucesso!")
    else:
        st.toast(":material/error: Planilha não pôde ser salva!")


def handle_hide() -> None:
    """Hides the dataframa stored in state"""
    if isinstance(state.df, DataFrame):
        state.df = False
    else:
        st.toast(":material/error: Aparentemente, não há planilha para remover da tela")


def handle_load() -> None:
    """loads the dataframa stored in file root"""
    state.df = statefull_dataframe_handler.get_df()
    if isinstance(state.df, DataFrame):
        st.toast(":material/cached: Planilha encontrada e carregada")
    else:
        st.toast(
            ":material/error: Ops... algo deu errado com o carregamento. Talvez não haja planilha salva"
        )


def handle_delete() -> None:
    """Del the dataframa stored in file root"""

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
    """Starts daemon task that send email"""
    if state.start_task():
        st.toast(":material/start: Rotina iniciada")
    else:
        st.toast(
            ":material/error: Ops... algo deu errado com o carregamento. Talvez não haja planilha salva"
        )


def handle_pause() -> None:
    """pauses daemon task that send email"""
    if state.kill_task():
        st.toast(":material/cancel: Rotina desativada")
        st.rerun()
    else:
        st.toast(":material/error: Aparentemente, não há rotina para desativar")


def handle_logout() -> None:
    """Logout system"""
    if not state.is_logged:
        st.toast(":material/cancel: Usuário não logado")
    else:
        state.is_logged = False
        st.toast(":material/logout: Usuário deslogado")


if __name__ == "__main__":

    # Interface principal da aplicação
    st.title("Controle de TEDs")

    if not state.is_logged:
        with st.form("Faça login", clear_on_submit=True):
            username = st.text_input(
                "Username",
                placeholder="Usename",
                autocomplete="",
                help="Nome de usuário",
            )
            pwd = st.text_input(
                "Senha",
                placeholder="senha",
                type="password",
                autocomplete=None,
                help="senha",
            )
            btn_sbm = st.form_submit_button("Logar", type="primary")
            if btn_sbm:
                if not state.check_login(username=username, pwd=pwd):
                    st.toast("Username ou senha incorretos!")
                else:
                    st.rerun()

    else:
        st.sidebar.title("Menu")
        always_run_components()
        st.sidebar.divider()
        st.sidebar.write(":material/draft: Arquivo")
        if isinstance(state.df, DataFrame):
            LABEL = ":material/upload: Carregar arquivo Excel"
        else:
            LABEL = ":material/upload: Carregar novo arquivo Excel"
        st.sidebar.file_uploader(
            label=LABEL,
            type=["xlsx"],
            on_change=dispatch,
            key="file_uploaded",
            kwargs={"func": "new"},
        )

        st.sidebar.button(
            ":material/file_save: Salvar",
            use_container_width=True,
            on_click=dispatch,
            help="Clique para salvar a planilha. A planilha somente será salva se houve carregamento prévio.",
            kwargs={"func": "save"},
        )
        st.sidebar.button(
            ":material/delete: Deletar",
            use_container_width=True,
            help="Apague uma planilha salva. Isso causará a desativação da rotina",
            on_click=dispatch,
            kwargs={"func": "delete"},
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
            on_click=dispatch,
            kwargs={"func": "load"},
        )
        st.sidebar.button(
            ":material/close: Fechar",
            use_container_width=True,
            help="Remova a planilha da tela",
            on_click=dispatch,
            kwargs={"func": "hide"},
        )

        st.sidebar.divider()
        st.sidebar.write(":material/task_alt: Rotina")
        st.sidebar.button(
            ":material/start: Iniciar",
            use_container_width=True,
            help="Inicia uma rotina, desde que haja planilha salva",
            on_click=dispatch,
            kwargs={"func": "start"},
        )
        st.sidebar.button(
            ":material/cancel: Interromper",
            use_container_width=True,
            help="Pausar a rotina. Clique em inicial rotina para continuar",
            on_click=dispatch,
            kwargs={"func": "pause"},
        )
        st.sidebar.divider()
        st.sidebar.write(":material/admin_panel_settings: Sistema")
        st.sidebar.button(
            ":material/logout: Deslogar",
            use_container_width=True,
            help="Deslogar",
            on_click=dispatch,
            kwargs={"func": "logout"},
        )
        max_timeout = st.sidebar.number_input(
            "Tempo de sessão",
            min_value=30,
            max_value=600,
            step=30,
            value=state.max_timeout,
        )
        if max_timeout:
            state.max_timeout = max_timeout
        state.restore_timeout()
        timeout_counter()
        # Exibe o DataFrame se ele existir
        if isinstance(state.df, DataFrame):
            st.dataframe(state.df, use_container_width=True)
            set_chart()
        else:
            st.write("Nenhuma planilha carregada.")
            st.image("assets/empty_state.jpg", caption="Não há planilhas", width=400)
