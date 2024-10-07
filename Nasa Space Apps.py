import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Define the logistic growth function
def logistic_growth(t, P0, K, r):
    return K / (1 + (K - P0) / P0 * np.exp(-r * t))

# Generate sample data
np.random.seed(42)
num_years = 150

# Initial population data
initial_population = 150
df = pd.DataFrame({
    'lat': np.random.uniform(-90, 90, initial_population // 1000),
    'lon': np.random.uniform(-180, 180, initial_population // 1000),
})

# Parameters for the logistic growth equation
K = 10000000  # Carrying capacity
r = 0.1  # Growth rate

# Simulate population changes over years
population_data = []
total_population = []
current_population = initial_population

for year in range(num_years):
    current_population = int(logistic_growth(year, initial_population, K, r))
    num_dots = current_population // 1000
    
    if num_dots > len(df):
        new_dots = num_dots - len(df)
        new_df = pd.DataFrame({
            'lat': np.random.uniform(-90, 90, new_dots),
            'lon': np.random.uniform(-180, 180, new_dots),
        })
        df = pd.concat([df, new_df], ignore_index=True)
    elif num_dots < len(df):
        df = df.iloc[:num_dots]
    
    population_data.append(df.copy())
    total_population.append(current_population)

# Create the Planet's surface
def create_Planet_surface():
    theta = np.linspace(0, 2*np.pi, 100)
    phi = np.linspace(0, np.pi, 50)
    x = 1 * np.outer(np.cos(theta), np.sin(phi))
    y = 1 * np.outer(np.sin(theta), np.sin(phi))
    z = 1 * np.outer(np.ones(100), np.cos(phi))
    return x, y, z

x, y, z = create_Planet_surface()

# Create the plot with two subplots
fig = make_subplots(
    rows=1, cols=2,
    specs=[[{'type': 'scene'}, {'type': 'xy'}]],
    column_widths=[0.7, 0.3],
    subplot_titles=("Planet Population Density", "Total Population Over Time")
)

# Add the Planet's surface
Planet_surface = go.Surface(x=x, y=y, z=z, colorscale='Blues', showscale=False)
fig.add_trace(Planet_surface, row=1, col=1)

# Create scatter plot for population data
scatter = go.Scatter3d(
    x=[],
    y=[],
    z=[],
    mode='markers',
    marker=dict(
        size=2,
        color='green',
        opacity=0.8
    ),
    text=[],
    hoverinfo='text'
)

fig.add_trace(scatter, row=1, col=1)

# Add initial total population graph
fig.add_trace(go.Scatter(x=[0], y=[total_population[0]], mode='lines', name='Total Population'), row=1, col=2)

# Create frames for animation
frames = []
for year, df in enumerate(population_data):
    frame = go.Frame(
        data=[
            Planet_surface,
            go.Scatter3d(
                x=(1.01 * np.cos(df['lon'] * np.pi / 180) * np.cos(df['lat'] * np.pi / 180)),
                y=(1.01 * np.sin(df['lon'] * np.pi / 180) * np.cos(df['lat'] * np.pi / 180)),
                z=1.01 * np.sin(df['lat'] * np.pi / 180),
                mode='markers',
                marker=dict(
                    size=2,
                    color='green',
                    opacity=0.8
                ),
                text=[f'Population: {total_population[year]}'] * len(df),
                hoverinfo='text'
            ),
            go.Scatter(x=list(range(year+1)), y=total_population[:year+1], mode='lines', name='Total Population')
        ],
        name=f'Year {year}'
    )
    frames.append(frame)

fig.frames = frames

# Update layout
fig.update_layout(
    title='Planet Population Density Model Over Time (Logistic Growth)',
    scene=dict(
        xaxis_title='',
        yaxis_title='',
        zaxis_title='',
        aspectmode='data'
    ),
    width=1200,
    height=600,
    margin=dict(r=10, l=10, b=10, t=40),
    updatemenus=[dict(
        type='buttons',
        showactive=False,
        buttons=[dict(label='Play',
                      method='animate',
                      args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True, mode='immediate')]),
                 dict(label='Pause',
                      method='animate',
                      args=[[None], dict(frame=dict(duration=0, redraw=True), mode='immediate')])]
    )],
    sliders=[dict(
        steps=[dict(method='animate',
                    args=[[f'Year {k}'], dict(mode='immediate', frame=dict(duration=100, redraw=True))],
                    label=f'Year {k}') for k in range(num_years)],
        transition=dict(duration=0),
        x=0,
        y=0,
        currentvalue=dict(font=dict(size=12), prefix='Year: ', visible=True, xanchor='right'),
        len=1.0
    )]
)

# Remove axes from 3D plot
fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)

# Update 2D graph layout
fig.update_xaxes(title_text="Year", row=1, col=2)
fig.update_yaxes(title_text="Total Population", row=1, col=2)

# Show the plot
fig.show()

fig.write_html("my_plot.html")