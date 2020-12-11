#include "ble.h"

#include "MicroBit.h"
// #include "radio.h"
#include "helper.h"
// #include "serial.h"

// #include <string>
// using namespace std;


bool is_empty_pdu(uint8_t * pdu_header, uint8_t pdu_hdrlen) {
    if (pdu_hdrlen != 2) {
        return false;
    }

    uint8_t llid_nesn_sn_md = pdu_header[0] & 0xF3; // Filter LSByte
    uint8_t pdu_length = pdu_header[1]; // MSByte 为 Length 字段。
    if (llid_nesn_sn_md == 0x01 // LLID 为 0b01，且其它字段为 0。
        && pdu_length == 0 // 要求仅为 Empty PDU。
    ) {
        return true;
    }
    else {
        return false;
    }
}


void dewhiten(uint8_t * data, int len, uint8_t channel)
{
    // Initialize LFSR Linear-Feedback Shift Register
    uint8_t lfsr = swap_bits(channel) | 0x02; // LFSR is 7-bit
    uint8_t c = 0;

    // 依次处理 data 中的每一个字节
    for (int i = 0; i < len; i++) {
        c = swap_bits(data[i]);

        // 依次处理 data[i] 中的每一个 bit
        for (int j = 7; j >= 0; j--) {
            if (lfsr & 0x80) { // LFSR 的 MSB 为 1
                /* 
                 * next P4 = P3 xor P6 = P3 xor 1
                 * next P0 = P6 = 1 xor LFSR_LSB = 1 xor 0
                 */
                lfsr ^= 0x11; 
                
                // data out = c (LSB first) xor P6 = c (LSB first) xor 1
                c ^= (1 << j);
            }
            
            /* 
             * 由于 0 xor n = n，所以当 LFSR 的 MSB 为 0 时，LFSR 直接左移 data
             * in 也等于 data out，不用做额外的处理。
             */

            lfsr <<= 1; // 移出 MSB P6, P6 = P5, P5 = P4... LFSR_LSB = 0
        }

        data[i] = swap_bits(c);
    }
}
