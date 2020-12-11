#pragma once

#include <stdint.h>

#define RF_RXBUF_MAX_LEN 254
#define RF_TXBUF_MAX_LEN 254

// Radio mode
#define MODE_IDLE 0
#define MODE_SNIFF_ADV 8 // Sniff advertising physical channel PDU


void radio_disable();

/*
 * Sniff advertising physical channel PDU.
 * 
 * channel 参数的取值为 37、38 或 39。
 *
 * Advertising physical channel PDU 的格式如下：
 * 
 *     +------------------+
 *     | Header | Payload |
 *     |--------|---------|
 *     | 16 b   | 1-255 B |
 *     +------------------+
 *
 * Header 字段的格式如下：
 *
 *     +-------------------------------------------------+
 *     | S0                                     | LENGTH |
 *     +-------------------------------------------------+
 *     | PDU Type | RFU | ChSel | TxAdd | RxAdd | Length |
 *     |----------|-----|-------|-------|-------|--------|
 *     | 4 b      | 1 b | 1 b   | 1 b   | 1 b   | 1 B    |
 *     +-------------------------------------------------+
 */
void radio_sniff_adv(uint8_t channel);


/*
 * Convert a BLE channel number into the corresponding frequency offset
 * for the nRF51822.
 */
uint8_t channel2freq(uint8_t channel);
