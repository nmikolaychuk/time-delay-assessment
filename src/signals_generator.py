import random
import math

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

        # Параметры для АМ-манипуляции
        # Амплитуда, дБ
        self.low_ampl = 1.
        self.high_ampl = 4.
        self.mod_coef = (self.high_ampl - self.low_ampl) / (self.high_ampl + self.low_ampl)

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
        self.signal_phase = 0

        print("BITS:", self.bits)

        x, y = [], []
        length_of_signal = round(self.bits_per_second * self.bits_count)
        w = 2. * math.pi * self.signal_freq

        for t in range(length_of_signal):
            # Смена амплитуды
            bit_index = int(t / self.bits_per_second)
            ampl_value = self.low_ampl if self.bits[bit_index] == 0 else self.high_ampl
            value = (1. + self.mod_coef * ampl_value) * math.sin(w * (t / self.sampling_rate))

            # Заполнение списка отсчетов\значений
            x.append(t)
            y.append(value)

        return x, y
