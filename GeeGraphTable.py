import io
import base64
import dash
from dash import dcc, html, dash_table
import matplotlib
import matplotlib.pyplot as plt
from pylab import arange
import numpy as np 
import pandas as pd

matplotlib.use('Agg')

pontos = []
cores_pontos = []  
cores_mensagens = []
mensagens = []

app = dash.Dash(__name__)
server = app.server

form_style = {
    'border': '2px solid #2E8B57',
    'border-radius': '10px',
    'padding': '20px',
    'background-color': '#F0F8FF',  # Alice Blue
    'margin': '20px',
    'font-family': 'Arial, sans-serif',
    'justify-content': 'center',
    'position': 'relative'  # Adicionando posição relativa para posicionamento absoluto da logo
}

label_style = {
    'margin-right': '10px',
    'font-size': '16px',
    'text-align': 'center'
}

input_style = {
    'margin-right': '10px',
    'padding': '5px',
    'font-size': '16px'
}

button_style = {
    'background-color': '#2E8B57',
    'color': 'white',
    'border': '2px solid #2E8B57',
    'border-radius': '5px',
    'padding': '10px 20px',
    'font-size': '16px',
    'cursor': 'pointer',
    'margin-top': '15px',
    'margin-left': '15px',
}

app.layout = html.Div(style={'background-color': '#E6E6FA'}, children=[
    html.H1('ResponsibleSteel - Requisito 10.6.3c (v. 2.0)', style={'color': '#2E8B57', 'text-align': 'center'}),
    html.Div(style=form_style, children=[
        html.Img(src="/assets/logo.png", style={'position': 'absolute', 'top': '20px', 'right': '20px', 'width': '100px'}),
        html.P('Favor utilizar PONTO no lugar da VÍRGULA',
               style={'font-weight': 'bold', 'font-size': '14px', 'text-align': 'center', 'margin-bottom': '10px'}),
        html.Label('Proporção de Sucata em decimal', style=label_style),
        dcc.Input(id='input-x', type='number', value=0.0, style=input_style),
        html.Label('Emissão de GEE em decimal', style=label_style),
        dcc.Input(id='input-y', type='number', value=0.0, style=input_style),
        html.Button('Calcular', id='button', style=button_style),
        html.Button('Limpar', id='limpar', style=button_style),
    ]),
    html.Div([
        html.Div(id='message-container', style={'flex': '1', 'text-align': 'left', 'margin-left': '20px'}),
        html.Div(id='graph-container', style={'flex': '1', 'margin-left': '20px'})
    ], style={'display': 'flex', 'margin-bottom': '20px'})
])

@app.callback(
    [dash.dependencies.Output('message-container', 'children'),
     dash.dependencies.Output('graph-container', 'children'),
     dash.dependencies.Output('input-x', 'value'),
     dash.dependencies.Output('input-y', 'value')],
    [dash.dependencies.Input('button', 'n_clicks'),
     dash.dependencies.Input('limpar', 'n_clicks')],
    [dash.dependencies.State('input-x', 'value'),
     dash.dependencies.State('input-y', 'value')]
)

def update_output(n_clicks_button, n_clicks_limpar, x, y):
    def generate_color():
        r = np.random.randint(100, 201)  
        g = np.random.randint(100, 201)  
        b = np.random.randint(100, 201)  
        return '#%02X%02X%02X' % (r, g, b)
    
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'button':
        if n_clicks_button is None:
            return '', [html.Img(src=gerar_grafico([], []))], x, y
        else:
            X = float(x)
            Y = float(y)

            pontos.append((X, Y))
            cor = generate_color()
            cores_pontos.append(cor)
            cores_mensagens.append(cor)

            # CALCULA QUANTO FALTA PARA CHEGAR A THRESHOLDE GEE (Y)
            Thresholders = []

            Th1 = (2.8 - (2.45*X)) - Y
            Th1 = round(Th1, 2)

            Th2 = (2.0 - (1.75*X)) - Y
            Th2 = round(Th2, 2)

            Th3 = (1.2 - (1.05*X)) - Y
            Th3 = round(Th3, 2)

            Th4 = (0.4 - (0.35*X)) - Y
            Th4 = round(Th4, 2)

            # CALCULA QUANTO FALTA PARA CHEGAR A THRESHOLDE SUCATA (X)
            Sucata = []

            Su1 = X - ((2.8 - Y) / 2.45)
            Sucata.append(round(Su1, 2))

            Su2 = X - ((2.0 - Y) / 1.75)
            Sucata.append(round(Su2, 2))

            Su3 = X - ((1.2 - Y) / 1.05)
            Sucata.append(round(Su3, 2))

            Su4 = X - ((0.4 - Y) / 0.35)
            Sucata.append(round(Su4, 2))

            # MENSAGENS NA TELA
            mensagem = []
            thresholds = [Th1, Th2, Th3, Th4]
            for i, th in enumerate(thresholds):
                if th < 0:
                    data = {
                        'Ref.': [f'Ponto {len(pontos)}'],
                        'X': [X],
                        'Y': [Y],
                        'Próximo Nível': [f'Thresholde {i + 1}'],
                        'ΔX': [abs(Sucata[i])],
                        'ΔY': [abs(round(th, 2))]  
                    }
                    mensagem.append(data)
                    break  #Adiciona apenas a threshold mais próxima

            mensagens.extend(mensagem)

            return mensagem_html(), graph_html(), x, y

    elif button_id == 'limpar':
        if n_clicks_limpar is not None:
            pontos.clear()
            cores_pontos.clear()
            cores_mensagens.clear()
            mensagens.clear()
            x, y = 0.0, 0.0
            return '', [html.Img(src=gerar_grafico([], []))], x, y

    return '', [html.Img(src=gerar_grafico(pontos, cores_pontos))], x, y

def gerar_grafico(pontos, cores_pontos):
    fig, ax = plt.subplots()

    x = arange(0, 1, 0.1)
    ax.plot(x, f1(x), color='red')
    ax.plot(x, f2(x), color='yellow')
    ax.plot(x, f3(x), color='green')
    ax.plot(x, f4(x), color='blue')

    # Marcação dos pontos inseridos
    ultima_cor = None  # Variável para armazenar a última cor utilizada
    for i, ponto in enumerate(pontos):
        X, Y = ponto
        if i < len(cores_pontos):
            cor = cores_pontos[i]
            # Se a cor atual for igual à anterior, passe para a próxima cor na lista
            if cor == ultima_cor:
                if i + 1 < len(cores_pontos):
                    cor = cores_pontos[i + 1]
            else:
                ultima_cor = cor  #Atualiza a última cor utilizada
        else:
            cor = 'black'  #Cor padrão caso não haja cores suficientes
        ax.plot(X, Y, '*', color=cor)  
        ax.annotate(f'{i+1}', xy=(X, Y), xytext=(X + 0.02, Y + 0.02), font='Arial, 12', color='black', weight='bold')

    ax.legend(['Thresholder 1', 'Thresholder 2', 'Thresholder 3', 'Thresholder 4'])

    ax.set_title('')
    ax.set_xlabel('Scrape share of metallica input (proportion) - X')
    ax.set_ylabel('GHG emissions intensity of crude steel - Y\n(t CO₂ e/tonne crude steel)')
    ax.grid()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    encoded_image = base64.b64encode(buffer.read()).decode()

    return 'data:image/png;base64,{}'.format(encoded_image)

def f1(x):
    return 2.8 - (2.45 * x)

def f2(x):
    return 2.0 - (1.75 * x)

def f3(x):
    return 1.2 - (1.05 * x)

def f4(x):
    return 0.4 - (0.35 * x)

def mensagem_html():
    if mensagens:
        while len(cores_mensagens) < len(mensagens):
            cores_mensagens.append(cores_mensagens[-1])
        
        table_data = []
        for msg, cor in zip(mensagens, cores_mensagens):
            msg_dict = {}
            for key, value in msg.items():
                if key != 'backgroundColor':
                    #Descompactando listas de valores e usando apenas o valor correspondente
                    msg_dict[key] = value[0]  #Aqui estamos assumindo que há apenas um valor na lista
            table_data.append(msg_dict)
        
        style_data_conditional = [
            {
                'if': {'row_index': i},
                'backgroundColor': cor
            } for i, cor in enumerate(cores_mensagens)
        ]

        return dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in table_data[0].keys()],
            data=table_data,
            style_data_conditional=style_data_conditional,
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_table={'overflowX': 'scroll'}
        )
    else:
        return html.Div(style={'display': 'none'})

def graph_html():
    return [
        html.Img(src=gerar_grafico(pontos, cores_pontos))
    ]

if __name__ == '__main__':
    app.run_server(debug=True)

