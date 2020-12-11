#include "MicroBit.h"

#include "timer.h"
#include "serial.h"


MicroBit uBit;


int main() {
    uBit.init();
    timer_init(); // Init BLE timer.
    serial_init();

    __SEV();
    __WFE();

    create_fiber(host_cmd_handler);
    release_fiber(); /* Release the main fiber and enter the scheduler which 
                        will manage the running of other fibers. */
}
