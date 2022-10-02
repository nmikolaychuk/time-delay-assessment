from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplGraphics(FigureCanvas):
    """
    Функция отрисовки
    """
    def __init__(self, dpi=100):
        self.fig = Figure(dpi=dpi, facecolor=(.94, .94, .94, 0.), figsize=(7, 3))

        # Добавление области графа
        self.ax1 = self.fig.add_subplot(111)
        self.add_text()

        # Инициализация
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Policy.Expanding,
                                   QtWidgets.QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)

    def add_text(self):
        """
        Инициализация графика.

        :return: None.
        """
        self.ax1.set_title("Опорный сигнал")
        self.ax1.set_xlabel("Отсчёты сигнала")
        self.ax1.set_ylabel("Значения сигнала")
        self.ax1.grid(linestyle="dotted", alpha=0.65)

    def plot_graph(self, x_list: list, y_list: list):
        """
        Построение графика функции.

        :param x_list: Список временный отсчётов.
        :param y_list: Список значений.
        :return: None.
        """
        self.ax1.plot(x_list, y_list, linestyle="-", markersize=2, color='r')
        self.ax1.margins(0.05, 0.05)

    def clear_plot(self):
        """
        Очистка области графика.

        :return: None.
        """
        self.ax1.clear()
        self.add_text()
