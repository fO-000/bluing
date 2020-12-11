#pragma once

#include "MicroBit.h"

// 最多只能设为 254
#define SERIAL_RX_BUF_SIZE 254
#define SERIAL_TX_BUF_SIZE 254

// #define CMD_LEN SERIAL_RX_BUF_SIZE // U -> L: OP 1 B + Len 1 B + 252 PDU
// #define EVT_LEN SERIAL_TX_BUF_SIZE // L -> U: OP 1 B + Len 1 B + 252 PDU

#define CMD_LEN 100
#define EVT_LEN 100
#define SERIAL_DMSG_BUF_SIZE 100


#define SERIAL_CMD_HDR_SIZE 3
#define CMD_PAYLOAD_MAX_SIZE 100
#define SERIAL_EVT_HDR_SIZE 3


#define OP_LEN 1

// Host command opcode
#define OP_RESET 0x00
#define OP_ACK 2
#define OP_IDLE 2
#define OP_SNIFF_ADV 0x0B

// Event opcode
#define EVT_READY 0
#define EVT_ERROR 1
#define EVT_ACK 2
#define EVT_NEW_ADV 0x0B
#define OP_VERBOSE 0xFE
#define EVT_DEBUG 0xFF

void serial_init();
void serial_clear_buf();

/*
 * This function is a filber
 */
void host_cmd_handler();


/*
 * Format of data from lower computer to upper computer
 * 
 *     +----------------+
 *     | Opcode  | Len  |
 *     |---------|------|
 *     | 0x00    | 0x00 |
 *     +----------------+
 */
void serial_ready(MicroBitSerialMode mode);


/*
 * Format of data from lower computer to upper computer
 * 
 *     +---------------------------+
 *     | Opcode  | Len | Msg       |
 *     |---------|-----|-----------|
 *     | 0xFF    | 1 B | Max 250 B |
 *     +---------------------------+
 */
// void serial_debug(ManagedString msg, MicroBitSerialMode mode);
void serial_debug(MicroBitSerialMode mode, const char *format, ...);


/*
 * Format of data from lower computer to upper computer
 * 
 *     +-----------------------+
 *     | Op  | Len | Msg       |
 *     |-----|-----|-----------|
 *     | 1 B | 1 B | Max 252 B |
 *     +-----------------------+
 */
void serial_error(ManagedString msg, MicroBitSerialMode mode);




/*
 * Format of data from lower computer to upper computer
 *     +--------------------------------+
 *     | Op  | Len    | Host Command Op |
 *     |-----|--------|-----------------|
 *     | 1 B | 0x0001 | 1 B             |
 *     +--------------------------------+
 */
void serial_ack(uint8_t cmd_op, MicroBitSerialMode mode);

// void Usart_Send_String(uint8_t *str);

void serial_tx();

/*
 * Fiber
 */
void serial_new_adv(void *channel);
