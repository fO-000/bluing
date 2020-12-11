#include "timer.h"
#include <nrf51.h>
#include <nrf51_bitfields.h>


#define TIMER_PRESCALER   4 // 1 MHz
#define IRQ_PRIORITY_HIGH 1


void timer_init(void)
{
	/* 
	 * Without this running the radio will be running off of the internal RC
	 * oscillator, which means the frequency will be way off and the reception
	 * poor. 
	 */
	if (NRF_CLOCK->EVENTS_HFCLKSTARTED == 0UL) {
		NRF_CLOCK->TASKS_HFCLKSTART = 1UL;
		while (NRF_CLOCK->EVENTS_HFCLKSTARTED == 0UL);
	}

	NRF_TIMER2->MODE = TIMER_MODE_MODE_Timer;
	NRF_TIMER2->BITMODE = TIMER_BITMODE_BITMODE_24Bit;
	NRF_TIMER2->PRESCALER = TIMER_PRESCALER;

	NRF_TIMER2->INTENCLR = TIMER_INTENCLR_COMPARE0_Msk
						| TIMER_INTENCLR_COMPARE1_Msk
						| TIMER_INTENCLR_COMPARE2_Msk
						| TIMER_INTENCLR_COMPARE3_Msk;

	NVIC_SetPriority(TIMER2_IRQn, IRQ_PRIORITY_HIGH);
	NVIC_ClearPendingIRQ(TIMER2_IRQn);
	NVIC_EnableIRQ(TIMER2_IRQn);
}
