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

        # Формирование информационных бит
        self.bits = self._get_bits()

        # Параметры для АМ
        # Амплитуда, дБ
        self.low_ampl = 1.
        self.high_ampl = 4.
        self.mod_coef = (self.high_ampl - self.low_ampl) / (self.high_ampl + self.low_ampl)

        # Параметры для ФМ
        # Индек модуляции
        self.mod_index = 2.
        self.low_freq = 2. * math.pi * self.signal_freq
        self.high_freq = self.mod_index * self.low_freq

    def _get_bits(self):
        """
        Формирование случайной битовой информационной последовательности.

        :return: None.
        """
        bits = []
        for i in range(int(self.bits_count)):
            x = random.randint(0, 1)
            bits.append(x)
        return bits

    def get_ampl_modulated_signal(self):
        """
        Построить амплитудно-манипулированный сигнал.

        :return: Списки x, y.
        """
        # Перегенерация случайных бит
        self.bits = self._get_bits()

        # Опорная частота, Гц
        signal_freq = self.signal_freq * 1000
        # Частота дискретизации, Гц
        sampling_rate = self.sampling_rate * 1000

        x, y = [], []
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

        for t in np.arange(0, signal_duration, timestep):
            # Смена амплитуды
            bit_index = int(t / bit_time)
            ampl_value = self.low_ampl if self.bits[bit_index] == 0 else self.high_ampl
            value = (1. + self.mod_coef * ampl_value) * math.sin(w * t)

            # Заполнение списка отсчетов\значений
            x.append(t)
            y.append(value)

        return x, y

    def get_fm2_modulated_signal(self):
        """
        Построить ФМ2-манипулированный сигнал.

        :return: Списки x, y.
        """
        # Перегенерация случайных бит
        self.bits = self._get_bits()

        # Опорная частота, Гц
        signal_freq = self.signal_freq * 1000
        # Частота дискретизации, Гц
        sampling_rate = self.sampling_rate * 1000

        x, y = [], []
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

        for t in np.arange(0, signal_duration, timestep):
            bit_index = int(t / bit_time)
            bipolar_bit = -1 if self.bits[bit_index] == 0 else 1
            arg = w * t
            value = bipolar_bit * math.sin(arg)

            # Заполнение списка отсчетов/значений
            x.append(t)
            y.append(value)

        return x, y

    def get_freq_modulated_signal(self):
        """
        Построить частотно-манипулированный сигнал.

        :return: Списки x, y.
        """
        # Перегенерация случайных бит
        self.bits = self._get_bits()
        self.signal_phase = 0

        # Опорная частота, Гц
        signal_freq = self.signal_freq * 1000
        # Частота дискретизации, Гц
        sampling_rate = self.sampling_rate * 1000
        # Частота, соответствующая логическому "0"
        low_freq = self.low_freq * 1000
        # Частота, соответствующая логическому "1"
        high_freq = self.high_freq * 1000

        x, y = [], []
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

        return x, y
