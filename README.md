# UniPagerNextion
Nextion Interface for UniPager
Basic Idea:
A programm to be written here connects to the websocket server of UniPager to get status information, like on the website supplied with the UniPager. Possible solution: https://github.com/eidheim/Simple-WebSocket-Server 

On the other side, it opens a configurable serial port (like /dev/ttyUSBx) and talks to Nextion display to show the data as on the website. As the onboard UART of the RasPi is already used for the C9000 Pager, a USB-->3,3V TLL converter like http://www.ebay.de/itm/311419365525 should be used.

For the first step, just displaying would be enough. Second step would be the enable also commands from the Nextion display to the RustPager, maybe with one of the keyboards. http://support.iteadstudio.com/support/discussions/topics/1000065449

