#include <nrf51.h>
#include <nrf51_bitfields.h>

// #include "MicroBit.h"

#include <stdint.h>
// #include <stdlib.h>
// #include <vector>
// #include <algorithm>
#include <string>

#include "ble.h"
#include "radio.h"
#include "helper.h"
#include "serial.h"

using namespace std;


extern uint8_t mode;

extern uint8_t rf_rxbuf[]; // RADIO Rx buffer
extern uint8_t rf_txbuf[]; // RADIO Tx buffer

extern bool adv_buf_ready;
extern uint16_t adv_buf_valid_len;
extern uint8_t adv_buf[];


/*
 * 该函数用于处理 NRF_RADIO instance 中各种 event 产生的中断。
 */
extern "C" void RADIO_IRQHandler(void) {
    //serial_debug("Entered RADIO_IRQHandler()", ASYNC);

    //uint32_t aa = 0;
    uint8_t pdu_header[PDU_HDR_LEN] = { 0 };
    string msg;

    if (NRF_RADIO->EVENTS_READY && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_READY_Msk
    ) {
        NRF_RADIO->EVENTS_READY = 0;
        //serial_debug("EVENTS_READY, Radio state: RXRU -> RXIDLE", ASYNC);
    }

    if (NRF_RADIO->EVENTS_ADDRESS && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_ADDRESS_Msk
    ) {
        NRF_RADIO->EVENTS_ADDRESS = 0;
        //serial_debug("EVENTS_ADDRESS, Radio state: RX", ASYNC);
    }

    if (NRF_RADIO->EVENTS_PAYLOAD && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_PAYLOAD_Msk
    ) {
        NRF_RADIO->EVENTS_PAYLOAD = 0;
        //serial_debug("EVENTS_PAYLOAD, Radio state: RX", ASYNC);
    }

    if (NRF_RADIO->EVENTS_END && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_END_Msk
    ) { // Radio state: RXIDLE <- RX
        NRF_RADIO->EVENTS_END = 0;

        switch (mode) {
            case MODE_SNIFF_ADV: {
                if (NRF_RADIO->CRCSTATUS == 1) {
                    if (!adv_buf_ready) {
                        adv_buf_valid_len = ADV_PHY_CH_PDU_HDR_SIZE + rf_rxbuf[1];
                        memcpy(adv_buf, rf_rxbuf, adv_buf_valid_len);
                        adv_buf_ready = true;
                    }
                }
                break;
            }

            default: {
                //serial_debug("Invalid radio mode", ASYNC);
            }
        }

        // 继续收发，并向 NRF_RADIO->PACKETPTR 。
        NRF_RADIO->TASKS_START = 1; // Radio state: RXIDLE -> RX
    }

    if (NRF_RADIO->EVENTS_DISABLED && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_DISABLED_Msk
    ) {
        NRF_RADIO->EVENTS_DISABLED = 0;
        //serial_debug("EVENTS_DISABLED", ASYNC);
    }

    if (NRF_RADIO->EVENTS_DEVMATCH && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_DEVMATCH_Msk
    ) {
        NRF_RADIO->EVENTS_DEVMATCH = 0;
        //serial_debug("EVENTS_DEVMATCH", ASYNC);
    }

    if (NRF_RADIO->EVENTS_DEVMISS && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_DEVMISS_Msk
    ) {
        NRF_RADIO->EVENTS_DEVMISS = 0;
        //serial_debug("EVENTS_DEVMISS", ASYNC);
    }

    if (NRF_RADIO->EVENTS_RSSIEND && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_RSSIEND_Msk
    ) {
        NRF_RADIO->EVENTS_RSSIEND = 0;
        //serial_debug("EVENTS_RSSIEND", ASYNC);
    }

    if (NRF_RADIO->EVENTS_BCMATCH && 
        NRF_RADIO->INTENSET & RADIO_INTENSET_BCMATCH_Msk
    ) {
        NRF_RADIO->EVENTS_BCMATCH = 0;
        //serial_debug("EVENTS_BCMATCH", ASYNC);
    }
}
