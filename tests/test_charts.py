import unittest
from matplotlib.backends.backend_agg import FigureCanvasAgg

from ui.charts import event_figure, spending_figure


class ChartTests(unittest.TestCase):
    def test_monthly_chart_renders_empty_and_populated_data_in_both_themes(self):
        for dark in (True, False):
            for counts in ([0,0,0,0,0,0], [1,0,3,7,2,1]):
                figure = event_figure([(f'2026-{i+1:02d}', count) for i,count in enumerate(counts)], dark)
                FigureCanvasAgg(figure).draw()
                self.assertEqual(list(figure.axes[0].lines[0].get_ydata()), counts)
                self.assertEqual(len(figure.axes[0].get_xticklabels()), 6)
                figure.clear()

    def test_spending_chart_renders_empty_and_populated_data_in_both_themes(self):
        for dark in (True, False):
            for values in ([], [('Loyer',1000), ('Un motif très long qui doit rester lisible',500)]):
                figure = spending_figure(values, dark)
                FigureCanvasAgg(figure).draw()
                self.assertEqual(len(figure.axes[0].patches), len(values))
                figure.clear()
