#include "helper.h"
#include "ble.h"


/*
 * Swap every bit of a byte.
 */
uint8_t swap_bits(uint8_t b)
{
    uint8_t o = 0;

    for (int i = 0; i < 8; i++) {
        o = o << 1;
        o |= (b & (1 << i)) ? 1 : 0;
    }

    return o;
}


uint32_t btle_reverse_crc(uint32_t crc, uint8_t *data, int len)
{
	uint32_t state = crc;
	uint32_t lfsr_mask = 0xb4c000;
	uint32_t ret;
    uint8_t cur;
	int i, j, top_bit;

	for (i = len - 1; i >= 0; --i) {
		cur = data[i];
		for (j = 0; j < 8; ++j) {
			top_bit = state >> 23;
			state = (state << 1) & 0xffffff;
			state |= top_bit ^ ((cur >> (7 - j)) & 1);
			if (top_bit)
				state ^= lfsr_mask;
		}
	}

	ret = 0;
	for (i = 0; i < 24; ++i)
		ret |= ((state >> i) & 1) << (23 - i);

	return ret;
}


/*
 * Parameters
 *     lfsr
 *         给该参数传递 CRC 的初始值即可。
 *         
 *         为了提高效率，该变量在算法内部被设计为如下存储格式：
 *             MSB                               LSB
 *             +-----------------------------------+
 *             | 31 | ... | 24  | ... | 1  | 0     |
 *             |-----------------------------------|
 *             |          | CRC MSB -> LSB |       |
 *             |-----------------------------------|
 *             |    |     | P23 |     | P0 | c_lsb |
 *             +-----------------------------------+
 *
 *     pdu
 *         指向原本在 SoC RAM 中存储的 BLE LL PDU。
 * 
 * Reference
 *     BLUETOOTH SPECIFICATION Version 4.2 [Vol 6, Part B] page 59, Figure 3.2:
 *     The LFSR circuit generating the CRC
 */
uint32_t gen_ble_ll_crc24(
    uint32_t lfsr, // crc24_init
    const uint8_t * pdu, uint16_t pdu_len
) {
    lfsr = lfsr << 1 & 0x01FFFFFE; // Initialize LFSR
    uint8_t c = 0; // Current byte

    for (int i = 0; i < pdu_len; i++) {
        c = pdu[i];

        for (int j = 0; j < 8; j++) {
            //uint8_t p23 = (lfsr & 0x01000000) >> 24;
            //uint8_t c_lsb = c & 0x01;
            if ((lfsr & 0x01000000) >> 24 ^ c & 0x01) { // p23 ^ c_lsb
                lfsr ^= 0x0000065A; // poly without MSB and LSB 0x0000032D << 1 
                lfsr |= 0x00000001; // 准备 P23 -> P0 = 1
            }

            c >>= 1;
            lfsr <<= 1;
        }
    }

    return (lfsr & 0x01FFFFFE) >> 1;
}
