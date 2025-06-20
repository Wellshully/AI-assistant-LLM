from wakeonlan import send_magic_packet
import config


def open_pc():
    send_magic_packet(config.PC_MAC)
