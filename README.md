# UniPagerNextion
Nextion Interface for UniPager
Basic Idea:
A programm to be written here connects to the websocket server of UniPager to get status information, like on the website supplied with the UniPager. We use Python

On the other side, it opens a configurable serial port (like /dev/ttyUSBx) and talks to Nextion display to show the data as on the website. As the onboard UART of the RasPi is already used for the C9000 Pager, a USB-->3,3V TLL converter like http://www.ebay.de/itm/311419365525 should be used.

Status: GUI is done, small cosmetical improvments are still possible. Reading Config from UniPager is done, wiriting config also.
Missing: Send paging message handling

Dependencies:
apt-get install python3 python3-websocket python3-serial
