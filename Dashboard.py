

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import numpy as np
import os

encoded_image = base64.b64encode(open(
    r"data/R.png", "rb"
).read()).decode()

# Inicializar app
app = dash.Dash(__name__)
app.title = "Dashboard de Control de Tiempos"

# --- Cargar datos principales ---
datos = pd.read_excel(
    "data/Control de tiempos (21).xlsx",
    engine="openpyxl"
)
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
df_proyectos = datos_fecha["Clave de la Auditoria"].unique()

# --- Datos presupuestados ---
datos_previstos = pd.read_excel(
    "data/Libro 2.xlsx",
    engine="openpyxl"
).iloc[:-1]

# --- Datos de control de horas ---
datos_jime = pd.read_excel(
    "data/Datos.xlsx",
    engine="openpyxl"
)

datos_jime["Control de horas"] = np.where(
    datos_jime["Horas presupuestadas"] != 0,
    datos_jime["Horas presupuestadas"] - datos_jime["Horas Incurridas"],0)
datos_jime["Horas presupuestadas restantes"] = datos_jime["Control de horas"].clip(lower=0)
datos_jime["Horas exedentes"] = datos_jime["Control de horas"].clip(upper=0)
datos_jime["Horas incurridas"] = datos_jime["Horas Incurridas"] + datos_jime["Horas exedentes"]

# --- Datos para la tabla de presupuestos ---
datos_tabla = pd.read_excel(
    "data/Horas_auditor.xlsx",
    engine="openpyxl"
)
datos_tabla2 = (
    datos_tabla[["Integrante", "Horas disponibles para proyectos"]]
    .dropna()
    .query("Integrante != 'Total'")
)
datos_tabla3 = datos_tabla[["Entidad", "Horas Presupuestas*",
                            "Horas Incurridas en proyectos al 30 de agosto de 2024"]].dropna()

datos_tabla4 = datos_tabla[["Integrante", "Horas disponibles para proyectos"]].dropna()

# --- Datos para la gráfica 4 ---
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

#Mapeos

mapeo1= ["004-RT,RCS,ISC-QCR", "047-Fact,RT-QS", "048-Fact,Susc-QES", "049-Reas,RT-QES",
         "067-IBNR,RRC-QIC", "072-Reaseg-QPE", "073-FAct,RT-QPE", "074-Ctar,RT,Msol,QPE",
         "083-Siniestro-QS", "107-IBNR,RRC-QIC", "114-ARSI-QMX", "115-PSolDin-QMX",
         "116-ARSI-QS", "117-PSolDin-QS", "137-RT-QCR", "139-Susc-QS", "148-Reaseg-QS"]

mapeo2 = {"AI-24-004" : "004-RT,RCS,ISC-QCR", "AI-24-047" : "047-Fact,RT-QS", 
          "AI-24-048" : "048-Fact,Susc-QES", "AI-24-049" : "049-Reas,RT-QES",
         "AI-24-067" : "067-IBNR,RRC-QIC", "AI-24-072" : "072-Reaseg-QPE", 
         "AI-24-073" : "073-FAct,RT-QPE", "AI-24-074" : "074-Ctar,RT,Msol,QPE",
         "AI-24-083" : "083-Siniestro-QS", "AI-24-107" : "107-IBNR,RRC-QIC", 
         "AI-24-114" : "114-ARSI-QMX", "AI-24-115" : "115-PSolDin-QMX",
         "AI-24-116" : "116-ARSI-QS", "AI-24-117" : "117-PSolDin-QS", 
         "AI-24-137" : "137-RT-QCR", "AI-24-139" : "139-Susc-QS", 
         "AI-24-148" : "148-Reaseg-QS"}

original1 = datos_jime["Proyectos"].tolist()

opciones_personalizadas = [
    {
        "label": mapeo2.get(p, p),  # si no está en el dict, cae en el mismo p
        "value": p
    }
    for p in datos_jime["Proyectos"].unique()
]

color_map = {
    "Carlos Alan Quiroz Herrera":        "#522D6D",
    "Guadalupe Ivonne Peñaloza Macías":  "#0091B3",
    "María Guadalupe Bravo Varela":      "#702DB3",
    "Martha Jimena Portillo Gutiérrez":  "#A7A4DF",
    # Para el caso de 'Horas presupuestadas restantes'
    "Horas presupuestadas restantes":    "#F2BC73"
}

# --- Layout ---
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Dashboard de Control de Tiempos",
                    style={'fontSize': '16px', 'margin': '0', 'color': 'white'}),
            html.H3("Filtrado por auditorías del Plan Anual 2024",
                    style={'fontSize': '12px', 'margin': '0', 'color': 'white'})
        ], style={'flex': '1'}),
        html.Img(
            src=f"data:image/jpeg;base64,{encoded_image}",
            style={'height': '50px', 'margin-left': 'auto'}
            )
    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

    html.Div([
        html.Label("Filtrar por Auditor:",
                   style={'fontSize': '10px', 'color': 'white'}),
        dcc.Dropdown(
            id="filtro-auditor",
            options=[{"label": a, "value": a} for a in auditores_unicos],
            placeholder="Selecciona un auditor (opcional)",
            clearable=True,
            style={"width": "40%", 'fontSize': '10px', 'height': '25px', 'marginBottom': '10px'}
        ),
        html.Label("Filtrar por Proyecto:", style={'fontSize':'10px','color':'white','marginLeft':'30px'}),
        dcc.Dropdown(
            id="filtro-proyecto",
            options=opciones_personalizadas,
            placeholder="Selecciona un proyecto (opcional)",
            clearable=True,
            style={'width':'40%', 'fontSize':'10px', 'height':'25px'}
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
    dcc.Graph(id="grafico-proyecto", style={'display':'none','height':'350px'}),

    html.Div(id="tabla-datos", style={'marginTop': '20px'})
], style={'backgroundColor': '#522D6D', 'minHeight': '100vh', 'padding': '10px'})


@app.callback(
    Output("grafico1", "figure"),
    Output("grafico2", "figure"),
    Output("grafico3", "figure"),
    Output("grafico4", "figure"),
    Output("grafico-proyecto", "figure"),
    Output("grafico-proyecto", "style"),
    Output("kpis", "children"),
    Output("tabla-datos", "children"),
    Output("tabla-datos", "style"),
    Output("contenedor-graficas", "style"),
    Input("filtro-auditor", "value"),
    Input("filtro-proyecto", "value"),
    Input("mostrar-tablas", "value")
)
def actualizar_dashboard(auditor_seleccionado, proyecto_seleccionado, mostrar_tablas):
    style_grid  = {'display': 'grid', 'gridTemplateColumns':'1fr 1fr', 'gap':'10px'}
    style_pie   = {'display': 'none'}
    style_table = {'display': 'none'}
    # Filtrado básico
    df_filtrado = datos_fecha.copy()
    if auditor_seleccionado:
        df_filtrado = df_filtrado[df_filtrado["Auditor"] == auditor_seleccionado]

    # KPIs
    total_horas = df_filtrado["Horas"].sum()
    total_registros = len(df_filtrado)
    kpis = html.Div([
        html.Div(f"Total de horas: {total_horas:.2f}", style={'margin': '2px', 'color': 'white'}),
        html.Div(f"Registros: {total_registros}", style={'margin': '2px', 'color': 'white'})
    ], style={'display': 'flex', 'gap': '10px'})

    # Helper compacto para barras
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

    # ---------- FIGURA 1 ----------
    if auditor_seleccionado:
        df_inc = (
            df_filtrado
            .groupby("Auditoria o Proyecto", as_index=False)["Horas"]
            .sum()
            .rename(columns={"Auditoria o Proyecto": "Proyecto", "Horas": "Incurridas"})
        )
        # Extraer código corto
        df_inc["Proyecto"] = df_inc["Proyecto"].str.extract(r'^(AI-\d{2}-\d{3})')

        fila = datos_tabla2.loc[
            datos_tabla2["Integrante"] == auditor_seleccionado,
            "Horas disponibles para proyectos"
        ]
        presupuesto_total = float(fila.iloc[0]) if not fila.empty else 0.0

        usadas = df_inc["Incurridas"].sum()
        restantes = max(presupuesto_total - usadas, 0)

        df_pie = pd.concat([
            df_inc.rename(columns={"Incurridas": "Horas"})[["Proyecto", "Horas"]],
            pd.DataFrame({"Proyecto": ["Disponible"], "Horas": [restantes]})
        ], ignore_index=True)
        
        df_pie["Proyecto_label"] = df_pie["Proyecto"].map(mapeo2).fillna("Disponible")

        fig1 = px.pie(
            df_pie,
            names="Proyecto_label",
            values="Horas",
            title="Horas presupuestadas e incurridas"
        )
        fig1.update_layout(
            margin=dict(l=20, r=10, t=25, b=10),
            font=dict(size=9, color='black'),
            title=dict(font=dict(size=10, color='black')),
            plot_bgcolor='#A7A4DF',
            paper_bgcolor='#A7A4DF'
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
    else:
        fig1 = px.bar(
            datos_jime,
            x="Proyectos",
            y=[
            "Horas incurridas",
            "Horas exedentes",
            "Horas presupuestadas restantes"],
            title="Control de Horas por Proyecto",
            barmode = "stack",
            color_discrete_sequence=["#F2BC73", "#D65D72", "#009877"]
        )
        fig1 = compacto(fig1)
        fig1.update_yaxes(
            range=[datos_jime["Horas Incurridas"].min()*1.1,
                   datos_jime["Horas Incurridas"].max()*1.1]
        )
        fig1.update_xaxes(tickvals=original1,
                          ticktext=mapeo1)

    # ---------- FIGURA 2 ----------
    resumen2 = df_filtrado.groupby(["Empresa", "Tipo de revisión"], as_index=False)["Horas"].sum()
    fig2 = compacto(px.bar(
        resumen2,
        x="Empresa",
        y="Horas",
        color="Tipo de revisión",
        title="Horas Incurridas por Entidad",
        barmode="group",
        color_discrete_sequence=["#2E4D2E", "#D65D72"]
    ))

    # ---------- FIGURA 3: ahora dinámico ----------
    if auditor_seleccionado:
        # incurridas por Empresa
        df_inc_ent = (
            df_filtrado
            .groupby("Empresa", as_index=False)["Horas"]
            .sum()
            .rename(columns={"Horas": "Incurridas", "Empresa": "Entidad"})
        )
        # mismo presupuesto total del auditor
        fila = datos_tabla2.loc[
            datos_tabla2["Integrante"] == auditor_seleccionado,
            "Horas disponibles para proyectos"
        ]
        presupuesto_total = float(fila.iloc[0]) if not fila.empty else 0.0
        usadas_ent = df_inc_ent["Incurridas"].sum()
        restantes_ent = max(presupuesto_total - usadas_ent, 0)
        # DataFrame para pie por Entidad
        df_pie_ent = pd.concat([
            df_inc_ent.rename(columns={"Incurridas": "Horas"})[["Entidad", "Horas"]],
            pd.DataFrame({"Entidad": ["Disponible"], "Horas": [restantes_ent]})
        ], ignore_index=True)
        fig3 = px.pie(
            df_pie_ent,
            names="Entidad",
            values="Horas",
            title="Horas presupuestadas e incurridas por Entidad"
        )
        fig3.update_layout(
            margin=dict(l=20, r=10, t=25, b=10),
            font=dict(size=9, color='black'),
            title=dict(font=dict(size=10, color='black')),
            plot_bgcolor='#A7A4DF',
            paper_bgcolor='#A7A4DF'
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
    else:
        resumen3 = datos_previstos.groupby("Entidad", as_index=False)["Horas Presupuestadas en 2024"].sum()
        fig3 = px.pie(
            resumen3,
            names="Entidad",
            values="Horas Presupuestadas en 2024",
            title="Distribución de Horas Presupuestadas por Entidad",
            color_discrete_sequence=["#941B80", "#0096AE", "#C3A454", "#0096AE", "#941B80"]
        )
        fig3.update_traces(textfont_size=9)
        fig3.update_layout(
            margin=dict(t=25, l=20, r=20, b=20),
            title_font_size=10,
            font=dict(color='black'),
            plot_bgcolor='#A7A4DF',
            paper_bgcolor='#A7A4DF'
        )

    # ---------- FIGURA 4 ----------
    df_jime_filtrado = datos_jime2.copy()
    if auditor_seleccionado:
        df_jime_filtrado = df_jime_filtrado[
            df_jime_filtrado["Auditor"] == auditor_seleccionado
        ]
    
    fig4 = compacto(px.bar(
        df_jime_filtrado,
        x="Proyectos",
        y="Horas",
        color="Auditor",
        title="Horas por Proyecto y Auditor",
        barmode="stack",
        # Aquí va el mapeo explícito
        color_discrete_map=color_map
    ))
    fig4.update_xaxes(tickvals=original1, ticktext=mapeo1)
    
    # ——— PASTEL POR PROYECTO ———
    # valores por defecto: oculto el pastel y mantengo el grid
    style_pie = {'display': 'none'}
    style_grid = {'display': 'grid',
                  'gridTemplateColumns':'1fr 1fr',
                  'gap':'10px'}
    fig_proj = go.Figure()

    if proyecto_seleccionado:
        # filtrar la fila del proyecto
        df_p = datos_jime[datos_jime["Proyectos"] == proyecto_seleccionado]
        if not df_p.empty:
            fila = df_p.iloc[0]
            auds = [
                "Carlos Alan Quiroz Herrera",
                "Guadalupe Ivonne Peñaloza Macías",
                "María Guadalupe Bravo Varela",
                "Martha Jimena Portillo Gutiérrez"
            ]
            # horas reales de cada auditor
            horas = [fila.get(a, 0) for a in auds]
            labels = auds.copy()
            sobrante = fila["Horas presupuestadas restantes"]
            if sobrante > 0:
                labels.append("Horas presupuestadas restantes")
                horas.append(sobrante)
            fig_proj = px.pie(
                names=labels,
                values=horas,
                title=f"Distribución de Horas – {proyecto_seleccionado}"
            )
            fig_proj.update_layout(
                margin=dict(l=20, r=10, t=25, b=10),
                font=dict(size=9, color='black'),
                title=dict(font=dict(size=10, color='black')),
                plot_bgcolor='#A7A4DF',
                paper_bgcolor='#A7A4DF'
                )

            fig_proj.update_traces(textposition='inside', textinfo='label+percent')
        # al haber proyecto, muestro solo el pastel
        style_pie = {'display': 'block'}
        style_grid = {'display': 'none'}
        style_table = {'display': 'none'}


    # Mostrar/ocultar contenedor de gráficas
    mostrar_graficas = (
        {"display": "none"} if "mostrar" in mostrar_tablas else {
            "display": "grid",
            "gridTemplateColumns": "1fr 1fr",
            "gap": "10px"
        }
    )

    # ---------- Tabla de datos ----------
    tabla_html = []
    if "mostrar" in mostrar_tablas:
        datos_comb = pd.concat([datos_tabla4, datos_tabla3], axis=1)
        tabla_html = dash_table.DataTable(
            data=datos_comb.to_dict("records"),
            columns=[{"name": i, "id": i} for i in datos_comb.columns],
            style_table={'overflowX': 'auto', 'backgroundColor': '#fff'},
            style_header={'backgroundColor': '#A7A4DF', 'color': 'black', 'fontWeight': 'bold'},
            style_cell={'fontSize': '10px', 'textAlign': 'left'}
        )
    if "mostrar" in mostrar_tablas:
        style_grid  = {'display': 'none'}   # oculta las gráficas
        style_pie   = {'display': 'none'}   # oculta el pastel
        style_table = {'display': 'block'}  # muestra la tabla


    
    return fig1, fig2, fig3, fig4, fig_proj, style_pie, kpis, tabla_html, style_table, style_grid


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 8051)))
