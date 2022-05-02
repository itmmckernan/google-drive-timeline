import plotly.express as px
import pandas as pd

df = pd.read_pickle('out.pkl')
df = df[df['start'] < df['end']]
fig = px.timeline(df, x_start="start", x_end="end", y="name")
fig.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
fig.show()