"""Matplotlib figures independent of Tk, allowing headless rendering checks."""
from textwrap import shorten

from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

COLORS = ['#18A8B8', '#5276CC', '#A180CE', '#C59B52', '#72A79D', '#7A8CA5']


def palette(dark):
    return ('#142033', '#EDF3FB', '#9CADC2', '#30435B') if dark else ('#FFFFFF', '#17283F', '#52647B', '#D9E3EF')


def event_figure(months, dark=True):
    surface, text, muted, grid = palette(dark)
    figure = Figure(figsize=(7, 2.7), dpi=100, facecolor=surface, layout='constrained')
    axes = figure.subplots()
    axes.set_facecolor(surface)
    labels = [key[5:]+'/'+key[:4] for key, _ in months]
    counts = [count for _, count in months]
    indices = list(range(len(months)))
    axes.plot(indices, counts, color=COLORS[0], linewidth=2.4, marker='o', markersize=6)
    axes.fill_between(indices, counts, color=COLORS[0], alpha=0.12)
    axes.set_xticks(indices, labels)
    axes.set_ylabel('Rendez-vous', color=muted, fontsize=11)
    axes.set_xlabel('Mois de la date prévue', color=muted, fontsize=11)
    axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    axes.set_ylim(0, max(1, max(counts, default=0))*1.2)
    axes.grid(axis='y', color=grid, alpha=0.7)
    axes.set_axisbelow(True)
    axes.tick_params(colors=muted, labelsize=10)
    for spine in axes.spines.values():
        spine.set_visible(False)
    for index, count in enumerate(counts):
        axes.annotate(str(count), (index, count), xytext=(0, 9), textcoords='offset points',
                      ha='center', color=text, fontsize=10)
    return figure


def spending_figure(spending, dark=True):
    surface, text, muted, _ = palette(dark)
    figure = Figure(figsize=(7, 3.2), dpi=100, facecolor=surface, layout='constrained')
    total = sum(amount for _, amount in spending)
    if total == 0:
        axes = figure.subplots()
        axes.text(0.5, 0.5, 'Aucun décaissement payé à afficher.', transform=axes.transAxes,
                  ha='center', va='center', color=muted, fontsize=12)
        axes.set_axis_off()
        return figure
    axes, legend_axes = figure.subplots(1, 2, gridspec_kw={'width_ratios': [1, 1]})
    axes.set_facecolor(surface)
    legend_axes.set_axis_off()
    fractions = [amount/total for _, amount in spending]
    wedges, _, _ = axes.pie(fractions, startangle=90, colors=COLORS[:len(spending)],
                            wedgeprops={'width': 0.36, 'edgecolor': surface, 'linewidth': 2},
                            autopct=lambda percent: f'{percent:.0f} %' if percent >= 5 else '',
                            pctdistance=0.82, textprops={'color': text, 'fontsize': 10})
    axes.text(0, 0.10, 'Total payé', ha='center', color=muted, fontsize=10)
    formatted_total = f'{total:,}'.replace(',', ' ')
    if len(formatted_total) > 18:
        formatted_total = f'{total:.3g}'
    axes.text(0, -0.12, formatted_total, ha='center', color=text, fontsize=12, fontweight='bold')
    labels = [shorten(reason, width=25, placeholder='…')+'\n'+f'{amount:,}'.replace(',', ' ')
              for reason, amount in spending]
    legend_axes.legend(wedges, labels, loc='center left', frameon=False,
                       labelcolor=text, fontsize=10, labelspacing=0.7)
    axes.set_aspect('equal')
    return figure
