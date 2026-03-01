import random


def should_drop_packet(loss_probability=0.1):
    return random.random() < loss_probability