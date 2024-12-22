from flask import Flask, render_template, request, redirect
from services.weather import get_weather_data, parse_weather_data
from services.yandex_geo import get_coordinates
from services.model import check_bad_weather
from dash import Dash, dcc, html, Input, Output, callback_context, ALL, ctx
import dash_leaflet
import plotly.graph_objs as go
import json

app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

cities = []

@app.route('/', methods=["GET", "POST"])
def index():
    global cities
    if request.method == "POST":
        try:
            # Получаем данные из формы
            start_city = request.form.get("start_city").strip()
            end_city = request.form.get("end_city").strip()
            days = int(request.form.get("days"))
            intermediate_cities = [
                city.strip() for city in request.form.getlist("intermediate_cities") if city.strip()
            ]

            # Проверяем ввод
            if start_city.lower() == end_city.lower():
                raise ValueError("Начальный и конечный города не должны совпадать!")

            cities = [{"name": start_city}, {"name": end_city}]
            for city in intermediate_cities:
                cities.insert(-1, {"name": city})

            # Получение данных для всех точек маршрута
            for city in cities:
                try:
                    lat, lon = get_coordinates(city["name"])
                    city["lat"] = lat
                    city["lon"] = lon
                    city["forecast"] = parse_weather_data(get_weather_data(lat, lon, days))
                except Exception as e:
                    raise ValueError(f"Ошибка для города '{city['name']}': {str(e)}")
            return redirect('/dash/')
            
        except Exception as e:
            return render_template("error.html", error=str(e)), 500
    return render_template("index.html")

dash_app.layout = html.Div([
    html.H1("Карта маршрута"),

    html.Div([
        dash_leaflet.Map(center=[50, 50], zoom=4, children=[
            dash_leaflet.TileLayer(),
            dash_leaflet.LayerGroup(id="markers-layer"),
            dash_leaflet.Polyline(id="route-line", positions=[])
        ], id="map", style={'width': '50vw', 'height': '50vh'}),

        html.Div(id='weather-graph-container', style={'width': '50vw', 'height': '50vh'})
    ], style={'display': 'flex', 'width': '100%', 'justify-content': 'space-between'}),

    html.Div([
        dcc.Dropdown(
            id='metric-dropdown',
            options=[
                {'label': 'Температура', 'value': 'temperature_2m'},
                {'label': 'Скорость ветра', 'value': 'windspeed_10m'},
                {'label': 'Вероятность осадков', 'value': 'precipitation_sum'}
            ],
            value='temperature_2m',
            clearable=False,
            style={'width': '50%'}
        ),

        dcc.Dropdown(
            id='days-dropdown',
            options=[
                {'label': '3 дня', 'value': 3},
                {'label': '5 дней', 'value': 5}
            ],
            value=3,
            clearable=False,
            style={'width': '50%'}
        )
    ], style={'width': '100%', 'marginTop': '10px', 'display': 'flex', 'justify-content': 'center'})
])


@dash_app.callback(
    [Output("markers-layer", "children"), Output("route-line", "positions")],
    Input('map', 'id')
)
def add_route_and_markers(_):
    city_markers = []
    route_positions = []

    for city in cities:
        # Исправлено: передаем название города, а не объект city
        coordinates = get_coordinates(city["name"])  
        if coordinates:
            route_positions.append(coordinates)
            marker = dash_leaflet.Marker(position=coordinates, children=[
                dash_leaflet.Tooltip(city["name"]),
                dash_leaflet.Popup([html.H3(city["name"]), html.P("")])
            ], id={'type': 'marker', 'index': city["name"]})
            city_markers.append(marker)
    return city_markers, route_positions


@dash_app.callback(
    Output("weather-graph-container", "children"),
    [Input("metric-dropdown", "value"), Input("days-dropdown", "value")],
    Input({'type': 'marker', 'index': ALL}, 'n_clicks')
)
def update_graph(selected_metric, days, _):
    city_name = cities[0]["name"] if len(cities) > 0 else None

    def replace_value(input_str):
        mapping = {
            'temperature_2m': 'Средняя температура',
            'max_temperature': 'Максимальная температура',
            'min_temperature': 'Минимальная температура',
            'precipitation_sum': 'Осадки',
            'wind_speed_max': 'Максимальная скорость ветра'
        }
        return mapping.get(input_str, input_str)

    metric_mapping = {
        'temperature_2m': 'mean_temperature',
        'temperature_2m_max': 'max_temperature',
        'temperature_2m_min': 'min_temperature',
        'precipitation_sum': 'precipitation_sum',
        'windspeed_10m': 'wind_speed_max'
    }

    if ctx.triggered_id and ctx.triggered_id != "metric-dropdown" and ctx.triggered_id != "days-dropdown":
        city_name = json.loads(callback_context.triggered[0]['prop_id'].split(".")[0])["index"]

    if city_name:
        city = next((city for city in cities if city["name"] == city_name), None)
        if city:
            weather_data = get_weather_data(city["lat"], city["lon"], days)
            if weather_data:
                parsed_data = parse_weather_data(weather_data)
                
                # Проверяем отображение метрики
                metric_key = metric_mapping.get(selected_metric)
                if not metric_key:
                    return html.Div("Выбранная метрика недоступна")

                dates = [data['date'] for data in parsed_data]
                values = [data.get(metric_key, None) for data in parsed_data]

                if not dates or not values or None in values:
                    return html.Div("Нет данных для отображения")

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(x=dates, y=values, mode='lines+markers', name=replace_value(selected_metric))
                )
                fig.update_layout(
                    title=f'{replace_value(selected_metric)} в {city_name} за {days} дней',
                    xaxis_title='Дата',
                    yaxis_title='Значение',
                    template='plotly_white'
                )
                return dcc.Graph(figure=fig)

    return html.Div("Выберите город для отображения графика")

     
if __name__ == "__main__":
    app.run(debug=True)
