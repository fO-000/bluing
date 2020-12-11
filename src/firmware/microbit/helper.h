#pragma once

#include <stdint.h>

uint32_t btle_reverse_crc(uint32_t crc, uint8_t * data, int len);


uint32_t gen_ble_ll_crc24(
    uint32_t crc_init,
    const uint8_t * pdu, uint16_t pdu_len
);

uint8_t swap_bits(uint8_t b);
