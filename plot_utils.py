import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


def melt_df_for_subplot(
        df, 
        x_vars=['week','company'], 
        y_vars=['num_scooter','daily_ride_per_scooter',],
        ):
    df_draw = pd.melt(df, id_vars=x_vars, value_vars=y_vars,
                      var_name='feature', value_name='value')
    return df_draw

def plot_features(title, df, x='week', y='driven_miles', hue='area', col='company', sharey=True, x_rotate=True, dec_bar=True, melt=False):
    '''
    Plot features of the dataframe
    Args:
        title: title of the plot (ex 'Fig 1. ...')
        df: dataframe
        x: 'week' or 'day' or 'hour'
        y: operational feature (e.g. 'driven_miles') or 'value' (when use after melt_df_for_subplot)
        hue: 'company' or 'area' or None
        col: 'feature' (when use after melt_df_for_subplot) or 'company' or None
        sharey: False or True
        x_rotate: True (x=week or day) or False (x=hour)
        dec_bar: True (highlight overlapped weeks, only for x=week) or False
        melt: True (when use after melt_df_for_subplot) or False
    '''
    g = sns.FacetGrid(df, hue=hue, col=col, legend_out=True, palette="tab10", sharey=sharey)
    g.map_dataframe(sns.lineplot, x=x, y=y)
    g.add_legend()

    if melt:
        g.set_titles("{col_name}").set_axis_labels('')

    if x_rotate and (x == 'week' or x == 'day'):
        g.set_xticklabels(rotation=45, ha='right')

    if dec_bar and x == 'week':
        # highlight overlapped weeks
        start = pd.to_datetime("2018-12-03")
        end   = pd.to_datetime("2018-12-24")

        # draw a semi-transparent gray rectangle on each facet
        for ax in g.axes.flatten():
            ax.axvspan(start, end, color="gray", alpha=0.3)

    plt.suptitle(title, y=1.05)
    plt.show()

def plot_heatmap(title, df, feature='num_ride'):
    '''
    Plot heatmap of the dataframe
    Args:
        title: title of the plot
        df: dataframe (df_day_hour)
        feature: 2D histogram bin entry
    '''
    fig = px.density_heatmap(
        df, x="hour", y="day", z=feature,
        facet_col="company",
        facet_row="area",
        range_x=[0,24], nbinsx=24, nbinsy=7, range_y=[-0.5,6.5], histnorm='probability',
        category_orders={"day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
        title=title,
        height=700
        )

    fig.layout.annotations = [
        ann for ann in fig.layout.annotations
        if ann.text != "area"
    ]

    fig.show()