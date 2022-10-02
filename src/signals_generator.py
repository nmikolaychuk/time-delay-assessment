import random
import math
import numpy as np

from defaults import *


class SignalGenerator:
    """
    Объект для генерации опорного сигнала
    """
    def __init__(self,
                 s_r=DEFAULT_SAMPLING_RATE, s_freq=DEFAULT_SIGNAL_FREQ,
                 b_count=DEFAULT_BITS_COUNT, bps=DEFAULT_BITS_PER_SECOND,
                 t_delay=DEFAULT_TIME_DELAY, snr=DEFAULT_SNR):

        # Параметры сигнала
        self.sampling_rate = float(s_r)
        self.signal_freq = float(s_freq)
        self.bits_count = float(b_count)
        self.bits_per_second = float(bps)
        self.time_delay = float(t_delay)
        self.snr = float(snr)
        self.signal_phase = 0.

        # Буферы для хранения сигналов
        self.bits = []
        self.general_signal = []
        self.modulated_signal = []
        self.research_signal = []

        # Параметры для АМ
        # Амплитуда, дБ
        self.low_ampl = 1.
        self.high_ampl = 0.5

        # Параметры для ФМ
        # Индек модуляции
        self.mod_index = 2.
        self.low_freq = 2. * math.pi * self.signal_freq
        self.high_freq = self.mod_index * self.low_freq

    def _generate_bits(self):
        """
        Формирование случайной битовой информационной последовательности.
        """
        self.bits.clear()
        for i in range(int(self.bits_count)):
            x = random.randint(0, 1)
            self.bits.append(x)

    def _get_signal_parameters(self):
        """
        Рассчитать параметры сигналов.
        """
        # Опорная частота, Гц
        signal_freq = self.signal_freq * 1000
        # Частота дискретизации, Гц
        sampling_rate = self.sampling_rate * 1000

        # Длительность одного бита
        bit_time = 1. / self.bits_per_second
        # Длительность сигнала
        signal_duration = bit_time * self.bits_count
        # Частота опорного сигнала
        w = 2. * math.pi * signal_freq
        # Количество отсчётов сигнала
        n = sampling_rate * signal_duration
        # Шаг времени
        timestep = signal_duration / n
        return signal_duration, timestep, bit_time, w

    def calc_triple_general_signal(self):
        """
        Получить утроенный опорный сигнал на другой частоте.
        """
        self.research_signal.clear()

        # Опорная частота, Гц
        signal_freq = self.signal_freq * 1000 * 0.95
        # Частота дискретизации, Гц
        sampling_rate = self.sampling_rate * 1000

        x, y = [], []
        # Длительность одного бита
        bit_time = 1. / self.bits_per_second
        # Длительность сигнала
        signal_duration = bit_time * self.bits_count * 3
        # Частота опорного сигнала
        w = 2. * math.pi * signal_freq
        # Количество отсчётов сигнала
        n = sampling_rate * signal_duration
        # Шаг времени
        timestep = signal_duration / n

        for t in np.arange(0, signal_duration, timestep):
            x.append(t)
            y.append(math.sin(w * t))

        self.research_signal = [x, y]

    def calc_general_signal(self):
        """
        Получить опорный сигнал.
        """
        self._generate_bits()
        self.general_signal.clear()

        x, y = [], []
        signal_duration, timestep, _, w = self._get_signal_parameters()
        for t in np.arange(0, signal_duration, timestep):
            x.append(t)
            y.append(math.sin(w * t))

        self.general_signal = [x, y]

    def calc_ampl_modulated_signal(self):
        """
        Построить амплитудно-манипулированный сигнал.
        """
        # Перегенерация случайных бит
        self._generate_bits()
        self.modulated_signal.clear()

        x, y = [], []
        signal_duration, timestep, bit_time, w = self._get_signal_parameters()
        for t in np.arange(0, signal_duration, timestep):
            # Смена амплитуды
            bit_index = int(t / bit_time)
            ampl_value = self.low_ampl if self.bits[bit_index] == 0 else self.high_ampl
            value = ampl_value * math.sin(w * t)

            # Заполнение списка отсчетов\значений
            x.append(t)
            y.append(value)

        self.modulated_signal = [x, y]

    def calc_fm2_modulated_signal(self):
        """
        Построить ФМ2-манипулированный сигнал.
        """
        # Перегенерация случайных бит
        self._generate_bits()
        self.modulated_signal.clear()

        x, y = [], []
        signal_duration, timestep, bit_time, w = self._get_signal_parameters()
        for t in np.arange(0, signal_duration, timestep):
            bit_index = int(t / bit_time)
            bipolar_bit = -1 if self.bits[bit_index] == 0 else 1
            arg = w * t
            value = bipolar_bit * math.sin(arg)

            # Заполнение списка отсчетов/значений
            x.append(t)
            y.append(value)

        self.modulated_signal = [x, y]

    def calc_freq_modulated_signal(self):
        """
        Построить частотно-манипулированный сигнал.
        """
        # Перегенерация случайных бит
        self._generate_bits()
        self.modulated_signal.clear()
        self.signal_phase = 0

        # Частота, соответствующая логическому "0"
        low_freq = self.low_freq * 1000
        # Частота, соответствующая логическому "1"
        high_freq = self.high_freq * 1000

        x, y = [], []
        signal_duration, timestep, bit_time, w = self._get_signal_parameters()
        for t in np.arange(0, signal_duration, timestep):
            # Смена частоты
            bit_index = int(t / bit_time)
            bit_value = -1 if self.bits[bit_index] == 0 else 1
            freq = low_freq if bit_value == -1 else high_freq
            value = math.sin(freq * t + self.signal_phase)
            self.signal_phase = freq * t

            # Заполнение списка отсчетов\значений
            x.append(t)
            y.append(value)

        self.modulated_signal = [x, y]

    def calc_research_signal(self):
        """
        Получить исследуемый сигнал, в котором присутствует сдвинутая копия опорного сигнала.
        """
        if not self.modulated_signal:
            return

        # Получение исследуемого сигнала (утроенный с измененной частотой)
        self.calc_triple_general_signal()
        # Полученые временной задержки
        time_delay = self.time_delay / 1000

        if time_delay > self.research_signal[0][-1] - self.modulated_signal[0][-1]:
            return

        # Замена участка исследуемого сигнала на манипулированный сигнал
        idx = 0
        for i in range(len(self.research_signal[0])):
            if self.research_signal[0][i] >= time_delay:
                idx = i
                break

        signal_len = len(self.modulated_signal[0])
        new_signal = self.research_signal[1][:idx] + self.modulated_signal[1] + self.research_signal[1][idx+signal_len:]
        self.research_signal[1] = new_signal
