import random
import matplotlib.pyplot as plt
from collections import deque

class Frame:
    def __init__(self, size, creation_time):
        self.size = size
        self.creation_time = creation_time

class Channel:
    def __init__(self, bandwidth, propagation_delay):
        self.bandwidth = bandwidth
        self.propagation_delay = propagation_delay
        self.busy = False
        self.current_station = None
        self.collision = False

class Station:
    def __init__(self, id, channel, p, frame_size_range=(1000, 20000)):
        self.id = id
        self.channel = channel
        self.p = p
        self.frame_size_range = frame_size_range
        self.queue = deque()
        self.backoff_counter = 0
        self.collision_counter = 0
        self.successful_transmissions = 0
        self.total_delay = 0
        self.total_bits_sent = 0

    def generate_frame(self, current_time):
        frame_size = random.randint(*self.frame_size_range)
        self.queue.append(Frame(frame_size, current_time))

    def attempt_transmission(self, current_time):
        if not self.queue:
            return False

        if not self.channel.busy and random.random() < self.p:
            if self.backoff_counter > 0:
                self.backoff_counter -= 1
                return False

            self.channel.busy = True
            self.channel.current_station = self
            return True

        return False

    def handle_collision(self):
        self.collision_counter += 1
        self.backoff_counter = random.randint(0, 2**min(10, self.collision_counter) - 1)

    def complete_transmission(self, current_time):
        frame = self.queue.popleft()
        self.successful_transmissions += 1
        self.total_delay += current_time - frame.creation_time
        self.total_bits_sent += frame.size
        self.collision_counter = 0

class Simulation:
    def __init__(self, num_stations, channel_bandwidth, propagation_delay, simulation_time, frame_generation_rate):
        self.channel = Channel(channel_bandwidth, propagation_delay)
        self.stations = [Station(f"Station_{i}", self.channel, 0.5) for i in range(num_stations)]
        self.simulation_time = simulation_time
        self.frame_generation_rate = frame_generation_rate

    def run(self):
        current_time = 0
        while current_time < self.simulation_time:
            # Generate frames
            for station in self.stations:
                if random.random() < self.frame_generation_rate:
                    station.generate_frame(current_time)

            # Attempt transmissions
            transmitting_stations = []
            for station in self.stations:
                if station.attempt_transmission(current_time):
                    transmitting_stations.append(station)

            # Handle collisions
            if len(transmitting_stations) > 1:
                self.channel.collision = True
                for station in transmitting_stations:
                    station.handle_collision()
                self.channel.busy = False
                self.channel.current_station = None
            elif len(transmitting_stations) == 1:
                transmitting_station = transmitting_stations[0]
                transmission_time = transmitting_station.queue[0].size / self.channel.bandwidth
                current_time += transmission_time
                transmitting_station.complete_transmission(current_time)
                self.channel.busy = False
                self.channel.current_station = None

            current_time += 1

    def calculate_metrics(self):
        total_throughput = sum(station.total_bits_sent for station in self.stations) / self.simulation_time
        avg_delay = sum(station.total_delay / station.successful_transmissions if station.successful_transmissions > 0 else 0 for station in self.stations) / len(self.stations)
        return total_throughput, avg_delay

def run_simulation_with_varying_p(num_stations, channel_bandwidth, propagation_delay, simulation_time, frame_generation_rate, p_values):
    throughputs = []
    delays = []

    for p in p_values:
        sim = Simulation(num_stations, channel_bandwidth, propagation_delay, simulation_time, frame_generation_rate)
        for station in sim.stations:
            station.p = p
        sim.run()
        throughput, delay = sim.calculate_metrics()
        throughputs.append(throughput)
        delays.append(delay)

    return throughputs, delays

def plot_results(p_values, throughputs, delays):
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(p_values, throughputs)
    plt.xlabel('p value')
    plt.ylabel('Throughput (bits/s)')
    plt.title('Throughput vs p value')

    plt.subplot(1, 2, 2)
    plt.plot(p_values, delays)
    plt.xlabel('p value')
    plt.ylabel('Average Delay (s)')
    plt.title('Average Delay vs p value')

    plt.tight_layout()
    plt.show()

# Simulation parameters
num_stations = 5
channel_bandwidth = 1000000  # 1 Mbps
propagation_delay = 0.01  # 10 ms
simulation_time = 1000  # seconds
frame_generation_rate = 0.01  # frames per second per station
p_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

throughputs, delays = run_simulation_with_varying_p(num_stations, channel_bandwidth, propagation_delay, simulation_time, frame_generation_rate, p_values)
plot_results(p_values, throughputs, delays)