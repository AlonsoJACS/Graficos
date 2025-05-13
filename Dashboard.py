

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table
import pandas as pd
import plotly.express as px

# Inicializar app
app = dash.Dash(__name__)
app.title = "Dashboard de Control de Tiempos"

# Cargar datos principales
datos = pd.read_excel("data/Control de tiempos (21).xlsx")
datos_persona = datos[datos["Auditor"].isin([
    "Carlos Alan Quiroz Herrera", 
    "Guadalupe Ivonne Peñaloza Macías", 
    "Ivette Arely Fragoso González",
    "Julio Abraham Cano Cruz",
    "María Guadalupe Bravo Varela",
    "Martha Jimena Portillo Gutiérrez"
])]
datos_persona["Clave de la Auditoria"] = datos_persona["Clave de la Auditoria"].fillna("")
datos_fecha = datos_persona[datos_persona["Clave de la Auditoria"].str.startswith("AI-24")]

# Datos presupuestados
datos_previstos = pd.read_excel("data/Libro 2.xlsx")
datos_previstos = datos_previstos.iloc[:-1]

# Datos de control de horas
datos_jime = pd.read_excel("data/Datos.xlsx")
datos_jime["Control de horas"] = datos_jime["Horas presupuestadas"] - datos_jime["Horas Incurridas"]
datos_jime["Horas presupuestadas restantes"] = datos_jime["Control de horas"].apply(lambda x: x if x > 0 else 0)

# Datos para la tabla
datos_tabla = pd.read_excel("data/Horas_auditor.xlsx")
datos_tabla2 = datos_tabla[["Integrante", "Horas disponibles para proyectos"]].dropna()
datos_tabla3 = datos_tabla[["Entidad", "Horas Presupuestas*"]].dropna()

# Preparar df para la gráfica 4
datos_jime2 = datos_jime.melt(
    id_vars=["Proyectos"],
    value_vars=[
        "Carlos Alan Quiroz Herrera", 
        "Guadalupe Ivonne Peñaloza Macías", 
        "María Guadalupe Bravo Varela", 
        "Martha Jimena Portillo Gutiérrez",
        "Horas presupuestadas restantes"
    ],
    var_name="Auditor",
    value_name="Horas"
)

auditores_unicos = datos_fecha["Auditor"].unique()

# Layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Dashboard de Control de Tiempos", style={'fontSize': '16px', 'margin': '0', 'color': 'white'}),
            html.H3("Filtrado por auditorías del Plan Anual 2024", style={'fontSize': '12px', 'margin': '0', 'color': 'white'})
        ], style={'flex': '1'}),
        html.Img(src="/assets/tu_logo.png", style={'height': '50px', 'margin-left': 'auto'})
    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

    html.Div([
        html.Label("Filtrar por Auditor:", style={'fontSize': '10px', 'color': 'white'}),
        dcc.Dropdown(
            id="filtro-auditor",
            options=[{"label": a, "value": a} for a in auditores_unicos],
            placeholder="Selecciona un auditor (opcional)",
            clearable=True,
            style={"width": "40%", 'fontSize': '10px', 'height': '25px', 'marginBottom': '10px'}
        ),
        dcc.Checklist(
            id="mostrar-tablas",
            options=[{"label": "Mostrar tabla", "value": "mostrar"}],
            value=[],
            style={'color': 'white', 'fontSize': '10px', 'marginTop': '5px'}
        )
    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'}),

    html.Div(id="kpis", style={'fontSize': '10px', 'color': 'white', 'marginBottom': '10px'}),

    html.Div([
        dcc.Graph(id="grafico1", style={'height': '250px'}),
        dcc.Graph(id="grafico2", style={'height': '250px'}),
        dcc.Graph(id="grafico3", style={'height': '250px'}),
        dcc.Graph(id="grafico4", style={'height': '250px'}),
    ], id="contenedor-graficas", style={
        "display": "grid",
        "gridTemplateColumns": "1fr 1fr",
        "gap": "10px"
    }),

    html.Div(id="tabla-datos", style={'marginTop': '20px'})
], style={'backgroundColor': '#522D6D', 'minHeight': '100vh', 'padding': '10px'})


@app.callback(
    Output("grafico1", "figure"),
    Output("grafico2", "figure"),
    Output("grafico3", "figure"),
    Output("grafico4", "figure"),
    Output("kpis", "children"),
    Output("tabla-datos", "children"),
    Output("contenedor-graficas", "style"),
    Input("filtro-auditor", "value"),
    Input("mostrar-tablas", "value")
)
def actualizar_dashboard(auditor_seleccionado, mostrar_tablas):
    df_filtrado = datos_fecha.copy()
    if auditor_seleccionado:
        df_filtrado = df_filtrado[df_filtrado["Auditor"] == auditor_seleccionado]

    total_horas = df_filtrado["Horas"].sum()
    total_registros = len(df_filtrado)
    kpis = html.Div([
        html.Div(f"Total de horas: {total_horas:.2f}", style={'margin': '2px', 'color': 'white'}),
        html.Div(f"Registros: {total_registros}", style={'margin': '2px', 'color': 'white'})
    ], style={'display': 'flex', 'gap': '10px'})

    def compacto(fig):
        fig.update_layout(
            margin=dict(l=20, r=10, t=25, b=10),
            font=dict(size=9, color='black'),
            title=dict(font=dict(size=10, color='black')),
            plot_bgcolor='#A7A4DF',
            paper_bgcolor='#A7A4DF'
        )
        fig.update_xaxes(color='black')
        fig.update_yaxes(color='black')
        return fig

    fig1 = px.bar(
        datos_jime,
        x="Proyectos",
        y="Control de horas",
        title="Control de Horas por Proyecto",
        color="Control de horas",
        color_continuous_scale=["#941B80", "#0096AE"]
    )
    fig1 = compacto(fig1)
    fig1.update_yaxes(range=[datos_jime["Control de horas"].min() * 1.1, datos_jime["Control de horas"].max() * 1.1])

    resumen2 = df_filtrado.groupby(["Empresa", "Tipo de revisión"], as_index=False)["Horas"].sum()
    fig2 = compacto(px.bar(
        resumen2,
        x="Empresa",
        y="Horas",
        color="Tipo de revisión",
        title="Horas por Empresa/Tipo Incurridas",
        barmode="group",
        color_discrete_sequence=["#2E4D2E", "#D65D72"]
    ))

    resumen3 = datos_previstos.groupby("Entidad", as_index=False)["Horas Presupuestadas en 2024"].sum()
    fig3 = px.pie(
        resumen3,
        names="Entidad",
        values="Horas Presupuestadas en 2024",
        title="Distribución de Horas Presupuestadas por Entidad",
        color_discrete_sequence=["#941B80", "#0096AE", "#C3A454", "#0096AE", "#941B80"]
    )
    fig3.update_traces(textfont_size=9)
    fig3.update_layout(margin=dict(t=25, l=20, r=20, b=20),
                       title_font_size=10,
                       font=dict(color='black'),
                       plot_bgcolor='#A7A4DF',
                       paper_bgcolor='#A7A4DF')

    df_jime_filtrado = datos_jime2.copy()
    if auditor_seleccionado:
        df_jime_filtrado = df_jime_filtrado[df_jime_filtrado["Auditor"] == auditor_seleccionado]
    fig4 = compacto(px.bar(
        df_jime_filtrado,
        x="Proyectos",
        y="Horas",
        color="Auditor",
        title="Horas por Proyecto y Auditor",
        barmode="stack",
        color_discrete_sequence=["#522D6D", "#0091B3", "#702DB3", "#A7A4DF", "#F2BC73"]
    ))

    # Mostrar u ocultar gráficas
    mostrar_graficas = {"display": "none"} if "mostrar" in mostrar_tablas else {
        "display": "grid",
        "gridTemplateColumns": "1fr 1fr",
        "gap": "10px"
    }

    # Tabla
    tabla_html = []
    if "mostrar" in mostrar_tablas:
        datos_comb = pd.concat([datos_tabla2, datos_tabla3], axis=1)
        tabla_html = dash_table.DataTable(
            data=datos_comb.to_dict("records"),
            columns=[{"name": i, "id": i} for i in datos_comb.columns],
            style_table={'overflowX': 'auto', 'backgroundColor': '#fff'},
            style_header={'backgroundColor': '#A7A4DF', 'color': 'black', 'fontWeight': 'bold'},
            style_cell={'fontSize': '10px', 'textAlign': 'left'}
        )

    return fig1, fig2, fig3, fig4, kpis, tabla_html, mostrar_graficas


if __name__ == "__main__":
    app.run(debug=True, port=8051)
