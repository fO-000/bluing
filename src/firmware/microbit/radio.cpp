#include "radio.h"

#include <nrf51.h>
#include <nrf51_bitfields.h>
#include <stdlib.h>

#include "MicroBit.h"
#include "helper.h"
#include "serial.h"
#include "ble.h"

uint8_t rf_rxbuf[RF_RXBUF_MAX_LEN]; // RADIO Rx buffer
uint8_t rf_txbuf[RF_TXBUF_MAX_LEN]; // RADIO Tx buffer
uint8_t mode;


uint8_t channel2freq(uint8_t channel) {
    if (channel == 37)
        return 2; // 2400 + 2 MHz
    else if (channel == 38)
        return 26;
    else if (channel == 39)
        return 80;
    else if (channel < 11)
        return 2*(channel + 2);
    else
        return 2*(channel + 3);
}


void radio_disable() {
    mode = MODE_IDLE;

    if (NRF_RADIO->STATE != 0) {
        /*
         * NRF_RADIO instance 的 STATE register 仅有一个 field STATE。该 STATE 
         * register 有 9 中情况。其中只有 NRF_RADIO->STATE 为 0 时表示 RADIO is
         * in the Disabled state。因此只有当 NRF_RADIO->STATE != 0 时，我们才继
         * 续执行。
         */

        /*
         * 如果说 NRF_RADIO instance 是 Nordic nRF51822 提供的东西。那么 NVIC, 
         * Nested Vector Interrupt Controller 则是 ARM Cortex-M0 提供的东西，遵
         * 循 Cortex Microcontroller Software Interface Standard (CMSIS)。同时
         * 使用 NVIC_DisableIRQ() 操作 peripheral 产生的中断也是 ARM Mbed OS 提
         * 供的通用接口。
         * 
         * 每一个 event 的发生都可能产生 interrupt，进而导致相关的处理函数被调
         * 用。这里我们禁用与 RADIO 相关的 interrupt request，即不再调用处理函
         * 数。注意这不影响 event 的发生。
         */
        NVIC_DisableIRQ(RADIO_IRQn);
        
        /* 
         * 将 NRF_RADIO instance 的 DISABLED event 置 0，从而等待新的 DISABLED 
         * event 发生。
         */
        NRF_RADIO->EVENTS_DISABLED = 0;
        NRF_RADIO->TASKS_DISABLE = 1; // Start Disable RADIO task.

        // 等待新的 DISABLED event 发生，从而确认 RADIO has been disabled.
        while (NRF_RADIO->EVENTS_DISABLED == 0);
    }
}


void radio_sniff_adv(uint8_t channel) {
    serial_debug(SYNC_SLEEP, "Entered radio_sniff_adv(), channel: %d", channel);

    radio_disable();
    mode = MODE_SNIFF_ADV;

    memset(rf_rxbuf, 0x00, sizeof(rf_rxbuf));
    NRF_RADIO->PACKETPTR = (uint32_t)rf_rxbuf;

    NRF_RADIO->FREQUENCY = channel2freq(channel);
    
    // Configure Access Address
    NRF_RADIO->PREFIX0 = (ADV_PHY_CH_PDU_AA & 0xff000000) >> 24;
    NRF_RADIO->BASE0 = (ADV_PHY_CH_PDU_AA & 0x00ffffff) << 8;
    NRF_RADIO->RXADDRESSES = 0x1; // Enable reception on logical address 0
    
    NRF_RADIO->MODE = RADIO_MODE_MODE_Ble_1Mbit << RADIO_MODE_MODE_Pos;
    
    // Configure advertising physical channel PDU header and payload field
    NRF_RADIO->PCNF0 = 1UL << RADIO_PCNF0_S0LEN_Pos | // Enable S0, 1 bytes
                       8UL << RADIO_PCNF0_LFLEN_Pos | // Enable LENGTH, 8 bits
                       0UL << RADIO_PCNF0_S1LEN_Pos; // Disable S1

    NRF_RADIO->PCNF1 = 254UL << RADIO_PCNF1_MAXLEN_Pos |
                       0UL << RADIO_PCNF1_STATLEN_Pos | // 仅使用 LENGTH 确定 packet 的长度
                       3UL << RADIO_PCNF1_BALEN_Pos | // BALEN 3 B + PREFIX 1 B = len(AA) 4 B
                       RADIO_PCNF1_ENDIAN_Little << RADIO_PCNF1_ENDIAN_Pos |
                       RADIO_PCNF1_WHITEEN_Enabled << RADIO_PCNF1_WHITEEN_Pos;
    NRF_RADIO->DATAWHITEIV = channel;
    
    // Configure CRC-24
    NRF_RADIO->CRCCNF = RADIO_CRCCNF_LEN_Three << RADIO_CRCCNF_LEN_Pos | // CRC-24
                        RADIO_CRCCNF_SKIPADDR_Skip << RADIO_CRCCNF_SKIPADDR_Pos; // AA 不参与 CRC-24
    NRF_RADIO->CRCINIT = ADV_PHY_CH_PDU_CRC_INIT;
    NRF_RADIO->CRCPOLY = 0x00065B; // 1 0000 0000 0000 0110 0101 1011

    // Disable interrupt on all evnets, then enable interrupt on END event
    NRF_RADIO->EVENTS_END = 0;
    NRF_RADIO->INTENCLR = 0xFFFFFFFFUL;
    NRF_RADIO->INTENSET = RADIO_INTENSET_END_Set << RADIO_INTENSET_END_Pos;

    NRF_RADIO->SHORTS = RADIO_SHORTS_READY_START_Msk;

    NVIC_ClearPendingIRQ(RADIO_IRQn);
    // NVIC_SetPriority(RADIO_IRQn, 3);
    NVIC_EnableIRQ(RADIO_IRQn);

    NRF_RADIO->TASKS_RXEN = 1; // Radio state: DISABLED -> RXRU
    // serial_debug("Radio state: DISABLED -> RXRU", SYNC_SLEEP);
}
