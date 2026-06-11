import matplotlib.pyplot as plt
import tempfile


class ChartRenderer:

    @staticmethod
    def render(chart_model):

        print("CHART RENDERER CALLED")
        print("Title:", chart_model.title)
        print("Categories:", chart_model.categories)

        fig, ax = plt.subplots()

        first_series = chart_model.series[0]

        print("Values:", first_series.values)

        ax.bar(
            chart_model.categories,
            first_series.values
        )

        ax.set_title(chart_model.title)

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        )

        plt.savefig(temp_file.name)

        plt.close()

        print("IMAGE SAVED:", temp_file.name)

        return temp_file.name