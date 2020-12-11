#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <vector>

using namespace std;

#define AA_LEN 4
#define CHM_LEN 5

#define HOPINCRE_LEN 1 // 实际上 hop increment 的长度为 5 bits
#define PDU_HDR_LEN 2 // for BLE LL data channel

/*
 * The Access Address for all Advertising Physical Channel PDUs except
 * AUX_SYNC_IND PDU and AUX_CHAIN_IND PDU. 这两个 PDU 都首次出现在 Bluetooth 5.0
 * 中。
 */
#define ADV_PHY_CH_PDU_AA 0x8E89BED6

/*
 * The CRCInit for all Advertising Physical Channel PDUs except AUX_SYNC_IND 
 * PDU and its subordinate set
 */
#define ADV_PHY_CH_PDU_CRC_INIT 0x555555
#define HOPSEQ_PERIOD 37

#define HOPINTER_LEN 2
#define MIN_HOPINTER 6

#define CHANNEL_TICKER_TIMEOUT 2000 // Millisecond, 39 * 1.25 ms * 37 = 1803.75

#define ADV_PHY_CH_PDU_MAX_SIZE 257 // Header 2 bytes + Payload 255 bytes
#define ADV_PHY_CH_PDU_HDR_SIZE 2


/*
 * LL data channel empty PDU 可以通过 PDU header 来判断。特征如下：
 *     +-------------------------------------------------------+
 *     | LLID | NESN 1-bit | SN 1-bit   | MD  | RFU   | Length |
 *     |------|------------|------------|-----|-------|--------|
 *     | 0b01 | Don't care | Don't care | 0b0 | 0b000 | 0b0000 |
 *     +-------------------------------------------------------+
 * 
 * 即当 MD 与 RFU 字段为 0 时有 empty PDU。
 */
bool is_empty_pdu(uint8_t * pdu_header, uint8_t pdu_hdrlen);

/*
 * BLE LL de-whitening
 *
 * LSB                     uint8_ lfsr                      MSB
 * +----------------------------------------------------------+
 * | N\A | P0 | P1          | P2 | P3 | P4 | P5 | P6          |
 * | N\A | 1  | channel MSB |    |    |    |    | channel LSB |
 * +----------------------------------------------------------+
 *
 * Channel 是 LFSR 的初始值，且仅占 6-bit 空间。6-bit 空间也足够表示 40 个 BLE
 * channels。在算法的实现中我们让 LFSR 的 LSB 恒为 0。这样当 P6 进入 P0 时，只
 * 需要计算 LFSR_LSB = P6 xor LFSR_LSB，最后 LFSR 左移时，P6 便顺利进入 P0。
 * 
 * Data whitening 与 de-whitening 必须使用完全相同的 LFSR：
 * 
 *                                                                        data in
 * ----------------------------------------------------------------------    ^
 * |                                       |                            |    |
 * |                                       v                            |    |
 * -----> P0 ----> P1 ----> P2 ----> P3 --xor--> P4 ----> P5 ----> P6 ----> xor
 *        LSB                                                      MSB       ^
 *                                                                           |
 *                                                                   data out (LSB first)
 */
void dewhiten(uint8_t * data, int len, uint8_t channel);
