#include <driver/gpio.h>
#include <rcp/core.h>

#define RCP_LED_GPIO GPIO_NUM_2

extern "C" void app_main()
{
	gpio_reset_pin(RCP_LED_GPIO);
	gpio_set_direction(RCP_LED_GPIO, GPIO_MODE_OUTPUT);
	gpio_set_level(RCP_LED_GPIO, 1);
}
