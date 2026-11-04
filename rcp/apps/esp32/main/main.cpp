#include "driver/gpio.h"

#define LED_GPIO GPIO_NUM_2

extern "C" void app_main()
{
	gpio_reset_pin(LED_GPIO);
	gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT);
	gpio_set_level(LED_GPIO, 1);
}
