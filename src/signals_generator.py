import random
import math
import numpy as np

from defaults import *
from enums import SignalType, ModulationType


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
        self.bits_count = int(b_count)
        self.bits_per_second = float(bps)
        self.time_delay = float(t_delay)
        self.snr = float(snr)
        self.signal_phase = 0.

        # Буферы для хранения сигналов
        self.bits = []
        self.general_signal = []
        self.modulated_signal = []
        self.research_signal = []
        self.correlation_signal = []

        # Параметры для АМ
        # Амплитуда, B
        self.low_ampl = 1.
        self.high_ampl = 0.5

        # Параметры для ФМ
        # Индекc модуляции
        self.mod_index = 2.

        # Расчет параметров
        # Минимальная и максимальная частота,Гц
        self.low_freq = 2. * math.pi * self.signal_freq
        self.high_freq = self.mod_index * self.low_freq

        # Параметры большого сигнала
        self.rsch_signal_freq = self.signal_freq
        self.rsch_bits_count = int(self.bits_count * 3)

    @staticmethod
    def _generate_bits(bits_count):
        """
        Формирование случайной битовой информационной последовательности.
        """
        bits = []
        for i in range(int(bits_count)):
            x = random.randint(0, 1)
            bits.append(x)

        return bits

    def recalc_parameters(self):
        """
        Пересчет параметров, задаваемых с окна.
        """
        # Минимальная и максимальная частота,Гц
        self.low_freq = 2. * math.pi * self.signal_freq
        self.high_freq = self.mod_index * self.low_freq

        # Параметры большого сигнала
        self.rsch_signal_freq = self.signal_freq
        self.rsch_bits_count = int(self.bits_count * 3)

    def _get_signal_parameters(self, sf: float, bits_count: int):
        """
        Рассчитать параметры сигналов.
        """
        # Длительность одного бита
        bit_time = 1. / self.bits_per_second
        # Длительность сигнала
        signal_duration = bit_time * bits_count
        # Частота опорного сигнала
        w = 2. * math.pi * sf
        # Количество отсчётов сигнала
        n = self.sampling_rate * signal_duration
        # Шаг времени
        timestep = signal_duration / n
        return signal_duration, timestep, bit_time, w

    def calc_modulated_signal(self, signal_type: SignalType, modulation_type: ModulationType):
        """
        Построить амплитудно-манипулированный сигнал.
        """
        self.signal_phase = 0
        # Характеристики сигнала в зависимости от его типа
        bits_count = self.bits_count
        signal_freq = self.signal_freq
        if signal_type == SignalType.RESEARCH:
            bits_count = self.rsch_bits_count
            signal_freq = self.rsch_signal_freq

        # Перегенерация случайных бит
        bits = self._generate_bits(bits_count)

        # Перегенерация случайных бит
        if signal_type == SignalType.GENERAL:
            self.bits = bits

        # Получение параметров сигнала
        x, y = [], []
        signal_duration, timestep, bit_time, w = self._get_signal_parameters(signal_freq, bits_count)
        for t in np.arange(0, signal_duration, timestep):
            # Получение текущего бита
            bit_index = int(t / bit_time)
            # Модуляция
            if modulation_type == ModulationType.AM:
                ampl_value = self.low_ampl if bits[bit_index] == 0 else self.high_ampl
                value = ampl_value * math.sin(w * t)
            elif modulation_type == ModulationType.FM:
                bipolar_bit = -1 if bits[bit_index] == 0 else 1
                value = bipolar_bit * math.sin(w * t)
            elif modulation_type == ModulationType.PM:
                bit_value = -1 if bits[bit_index] == 0 else 1
                freq = self.low_freq if bit_value == -1 else self.high_freq
                value = math.sin(freq * t + self.signal_phase)
                self.signal_phase = freq * t
            else:
                return None, None

            # Заполнение списка отсчетов\значений
            x.append(t)
            y.append(value)

        return x, y

    def calc_research_signal(self):
        """
        Получить исследуемый сигнал, в котором присутствует сдвинутая копия опорного сигнала.
        """
        if not self.modulated_signal or not self.research_signal:
            return

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

    @staticmethod
    def _calc_signal_energy(signal: list):
        """
        Расчет энергии сигнала
        """
        energy = 0.
        for i in range(len(signal[1])):
            energy += signal[1][i] ** 2
        return energy

    @staticmethod
    def _get_random_value():
        """
        Рандомизация чисел для шума
        """
        av = 12
        value = 0.
        for i in range(av):
            value += random.uniform(-1, 1)
        return value / av

    def generate_noise(self, signal_type: SignalType):
        """
        Генерация шума для сигнала
        """
        snr = None
        signal = None
        if signal_type == SignalType.GENERAL:
            snr = 10
            signal = self.modulated_signal
        elif signal_type == SignalType.RESEARCH:
            snr = self.snr
            signal = self.research_signal

        if not signal:
            return

        # Расчет энергии сигнала
        signal_energy = self._calc_signal_energy(signal)
        # Расчет энергии шума
        noise_energy = signal_energy / (10 ** (snr / 10))
        # Процент шума
        noise_percent = signal_energy / noise_energy / 100.

        # Случайная шумовая добавка к каждому отсчету
        noise = []
        random_energy = 0.
        for i in range(len(signal[1])):
            random_value = self._get_random_value()
            noise.append(random_value)
            random_energy += random_value ** 2

        # Разброс шума
        alpha = math.sqrt(noise_percent * signal_energy / random_energy)
        # Зашумленный сигнал
        noise_signal = []
        for i in range(len(signal[1])):
            noise_signal.append(signal[1][i] + alpha * noise[i])

        return signal[0], noise_signal

    def get_correlation(self):
        """
        Расчет взаимной корреляционной функции опорного и исследуемого сигналов.
        """
        if not self.modulated_signal or not self.research_signal:
            return

        # Очистка буфера
        self.correlation_signal.clear()

        x, y = [], []
        small_signal_length = len(self.modulated_signal[0])
        big_signal_length = len(self.research_signal[0])
        for i in range(0, big_signal_length - small_signal_length - 1):
            summary = 0.
            for j in range(small_signal_length):
                summary += self.modulated_signal[1][j] * self.research_signal[1][i + j]

            x.append(i)
            y.append(summary)

        self.correlation_signal = [x, y]
