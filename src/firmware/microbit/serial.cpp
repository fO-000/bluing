#include "serial.h"

#include <nrf51.h>
#include <nrf51_bitfields.h>

#include <stdint.h>
#include <stdlib.h>
#include <string>
#include <stdarg.h>
using namespace std;

#include "MicroBit.h"
#include "radio.h"
#include "ble.h"

extern MicroBit uBit;

extern uint8_t rf_txbuf[];

uint8_t event[EVT_LEN];

bool adv_buf_ready = false;
uint16_t adv_buf_valid_len = 0;
uint8_t adv_buf[ADV_PHY_CH_PDU_MAX_SIZE];

uint8_t adv_channel; // from --channel=<num> option


void serial_init() {
    uBit.serial.baud(115200);
    while (uBit.serial.setRxBufferSize(SERIAL_RX_BUF_SIZE) != MICROBIT_OK) {uBit.sleep(10);}
    while (uBit.serial.setTxBufferSize(SERIAL_TX_BUF_SIZE) != MICROBIT_OK) {uBit.sleep(10);}

    // int rx_buf_size = uBit->serial.getRxBufferSize();
    // uBit->serial.send(("[Debug] Serial rx buf size: " + std::to_string(rx_buf_size) + " B\n").c_str());
    // int tx_buf_size = uBit->serial.getTxBufferSize();
    // uBit->serial.send(("[Debug] Serial tx buf size: " + std::to_string(tx_buf_size) + " B\n").c_str());
    serial_clear_buf();
}


void serial_clear_buf() {
    while (uBit.serial.clearRxBuffer() != MICROBIT_OK) {uBit.sleep(10);}
    while (uBit.serial.clearTxBuffer() != MICROBIT_OK) {uBit.sleep(10);}
}


void host_cmd_handler() {
    serial_debug(SYNC_SLEEP, "Entered host_cmd_handler fiber");
    serial_ready(SYNC_SLEEP);

    while (true) {
        uint8_t header[SERIAL_CMD_HDR_SIZE] = {0x00};
        int result = uBit.serial.read(header, sizeof(header), SYNC_SLEEP);
        if (result == MICROBIT_SERIAL_IN_USE) {
            uBit.sleep(10);
            continue;
        }
        else if (result != SERIAL_CMD_HDR_SIZE) {
            serial_error("Invalid command header", SYNC_SLEEP);
            serial_clear_buf();
            continue;
        }

        uint8_t opcode = header[0];
        uint16_t len = (header[1] << 8) + header[2];

        uint8_t payload[len] = {0x00};
        while ((result = uBit.serial.read(payload, len, SYNC_SLEEP)) == MICROBIT_SERIAL_IN_USE) {
            uBit.sleep(10);
        }
        if (result != len) {
            serial_error("Invalid command len", SYNC_SLEEP);
            serial_clear_buf();
            continue;
        }

        switch (opcode) {
            // case OP_IDLE: {
            //     //serial_debug("OP_IDLE", SYNC_SLEEP);
            //     channel_ticker.detach();
            //     hop_ticker.detach();
            //     radio_disable();
            //     serial_ack(OP_IDLE, SYNC_SLEEP);
            //     break;
            // }

            case OP_RESET: {
                serial_debug(SYNC_SLEEP, "OP_RESET");
                // radio_disable();
                // serial_clear_buf();
                uBit.reset();
                break;
            }

            case OP_SNIFF_ADV: { // Sniff advertising physical channel PDU
                //serial_debug("OP_SNIFF_ADV", SYNC_SLEEP);
                adv_channel = payload[0];
                create_fiber(serial_new_adv, (void*)&adv_channel);
                radio_sniff_adv(adv_channel);
                break;
            }

            // case OP_READY: {
            //     serial_debug(SYNC_SLEEP, "OP_READY");
            //     channel_ticker.detach();
            //     hop_ticker.detach();
            //     radio_disable();
            //     serial_ack(OP_READY, SYNC_SLEEP);
            //     break;
            // }

            default: {
                serial_error("Unknown upper opcode!", SYNC_SLEEP);
            }
        }
    }
}


void serial_new_adv(void *channel) {
    serial_debug(SYNC_SLEEP, "Entered serial_new_adv fiber, channel: %d", *((uint8_t*)channel));

    while (true) {
        if (adv_buf_ready) {
            uint8_t event[SERIAL_EVT_HDR_SIZE+adv_buf_valid_len] = {0x00};

            event[0] = EVT_NEW_ADV;
            event[1] = adv_buf_valid_len >> 8;
            event[2] = adv_buf_valid_len & 0xFF;
            memcpy(event+SERIAL_EVT_HDR_SIZE, adv_buf, adv_buf_valid_len);
            uBit.serial.send(event, sizeof(event), SYNC_SLEEP);
            adv_buf_valid_len = 0;
            adv_buf_ready = false;
        }
        uBit.sleep(0);
    }
}


void serial_ready(MicroBitSerialMode mode) {
    uint8_t event[SERIAL_EVT_HDR_SIZE] = {0x00};

    event[0] = EVT_READY;
    event[1] = 0x00;
    event[2] = 0x00;

    while (uBit.serial.send(event, sizeof(event), mode) == MICROBIT_SERIAL_IN_USE) {
        uBit.sleep(10);
    }
}


void serial_debug(MicroBitSerialMode mode, const char* format, ...) {
    char dmsg[SERIAL_DMSG_BUF_SIZE] = {0};
    va_list valist;

    va_start(valist, format);
    vsnprintf(dmsg, SERIAL_DMSG_BUF_SIZE, format, valist);
    va_end(valist);

    uint16_t len = strlen(dmsg);
    uint8_t event[SERIAL_EVT_HDR_SIZE+len] = {0};
    event[0] = EVT_DEBUG;
    event[1] = len >> 8 & 0xFF;
    event[2] = len & 0xFF;
    memcpy(event + SERIAL_EVT_HDR_SIZE, dmsg, len);

    while (uBit.serial.send(event, sizeof(event), mode) == MICROBIT_SERIAL_IN_USE) {
        uBit.sleep(10);
    }
}


void serial_error(ManagedString msg, MicroBitSerialMode mode) {
    uint16_t length = msg.length();
    uint8_t event[length] = {0x00};

    event[0] = EVT_ERROR;
    event[1] = length >> 8 & 0xFF;
    event[2] = length & 0xFF;
    memcpy(event + SERIAL_EVT_HDR_SIZE, msg.toCharArray(), length);

    while (uBit.serial.send(event, sizeof(event), mode) == MICROBIT_SERIAL_IN_USE) {
        uBit.sleep(10);
    }
}


void serial_ack(uint8_t cmd_op, MicroBitSerialMode mode) {
    // uint8_t event[4] = {0x00};
    // event[0] = EVT_ACK;
    // event[1] = 0x00;
    // event[2] = 0x01;
    // event[3] = cmd_op;

    // while (uBit.serial.send(event, sizeof(event), mode) == MICROBIT_SERIAL_IN_USE) {uBit.sleep(10);}
}


//初始化
// void Usart_Init(uint32_t bound)
// {
//     nrf_gpio_cfg_input(USART_RX, NRF_GPIO_PIN_NOPULL);
//     nrf_gpio_cfg_output(USART_TX);

//     NRF_UART0->PSELRXD = USART_RX;
//     NRF_UART0->PSELTXD = USART_TX;
//     NRF_UART0->PSELRTS = 0XFFFFFFFF;//关闭流控
//     NRF_UART0->PSELCTS = 0XFFFFFFFF;

//     NRF_UART0->BAUDRATE = bound;
//     NRF_UART0->CONFIG = 0;  //不使用流控,不校验

//     NRF_UART0->EVENTS_RXDRDY = 0;
//     NRF_UART0->EVENTS_TXDRDY = 0;

//     NRF_UART0->ENABLE = 4;  //使能串口
//     NRF_UART0->TASKS_STARTRX  = 1;
//     NRF_UART0->TASKS_STARTTX = 1;
// }

// //发送数据
// void Usart_Send_Byte(uint8_t dat)
// { 

//     NRF_UART0->EVENTS_TXDRDY = 0;
//     NRF_UART0->TXD = dat;
//     while(NRF_UART0->EVENTS_TXDRDY == 0);
// }

// //接收数据
// uint8_t Usart_Recive_Byte(void)
// {

//     while(NRF_UART0->EVENTS_RXDRDY == 0);
//     NRF_UART0->EVENTS_RXDRDY = 0;   //清零事件

//     return (uint8_t)NRF_UART0->RXD; 
// }

// //发送字符串
// void Usart_Send_String(uint8_t *str)
// {
//     uint8_t i = 0;

//     while(str[i] != 0x17)
//     {
//         Usart_Send_Byte(str[i]);
//         i++;
//     }

//     Usart_Send_Byte(0x17);
// }
