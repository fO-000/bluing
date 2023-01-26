#include "MicroBit.h"

#include "timer.h"
#include "serial.h"


MicroBit uBit;


int main() {
    uBit.init();
#ifdef YOTTA_CFG_TXPIN
  #ifdef YOTTA_CFG_RXPIN
    #pragma message("Bluing firmware will use custom serial pins")
    uBit.serial.redirect(YOTTA_CFG_TXPIN, YOTTA_CFG_RXPIN);
  #endif
#endif
    timer_init(); // Init BLE timer.
    serial_init();

    __SEV();
    __WFE();

    create_fiber(host_cmd_handler);
    release_fiber(); /* Release the main fiber and enter the scheduler which 
                        will manage the running of other fibers. */
}
