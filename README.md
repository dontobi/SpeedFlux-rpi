


# SpeedFlux <img src='https://user-images.githubusercontent.com/3665468/119735610-974a0500-be4a-11eb-9149-dd12ceee03df.png' width='75'>
---

SpeedFlux will monitor your internet speeds at a regular interval and export all of the data to InfluxDB.

It is mostly written in Python but, uses Ookla's SpeedTest CLI. This is a CLI app. We use Python subprocess to utilize this tool.

There are other Python packages out there that can use Ookla's systems but they are not official and don't provide the same data. This method is consistent and also provides several additional pieces of info. That extra info allows us to tag the data we send to InfluxDB many different ways.

You can see on the Grafana image below some examples of those tags such as averageing the speeds of different testing sites and rank them.
Other uses may tagging different interfaces and running an instance for each. [You can view those tagging options below](https://github.com/breadlysm/speedtest-to-influxdb/blob/master/README.md#tag-options)

 The grafana image below is a prebuilt dashboard you can find at https://grafana.com/grafana/dashboards/13053.

![OriginalDash](https://user-images.githubusercontent.com/3665468/116284820-8038ca00-a75b-11eb-9b30-4a9d26434f8d.png)

## Configuring the script

The InfluxDB connection settings are controlled by environment variables.

The variables available are:
- NAMESPACE = default - None
- INFLUX_DB_ADDRESS = default - influxdb
- INFLUX_DB_PORT = default - 8086
- INFLUX_DB_USER = default - {blank}
- INFLUX_DB_PASSWORD = default - {blank}
- INFLUX_DB_DATABASE = default - speedtests
- INFLUX_DB_TAGS = default - None * See below for options, '*' widcard for all *
- SPEEDTEST_INTERVAL = default - 5 (minutes)
- SPEEDTEST_SERVER_ID = default - {blank} * id from https://c.speedtest.net/speedtest-servers-static.php *
- PING_INTERVAL = default - 5 (seconds)
- PING_TARGETS = default - 1.1.1.1, 8.8.8.8 (csv of hosts to ping)
- LOG_TYPE = info

### Variable Notes
- Intervals are in minutes. *Script will convert it to seconds.*
- If any variables are not needed, don't declare them. Functions will operate with or without most variables.
- Tags should be input without quotes. *INFLUX_DB_TAGS = isp, interface, external_ip, server_name, speedtest_url*
- NAMESPACE is used to collect data from multiple instances of the container into one database and select which you wish to view in Grafana. i.e. I have one monitoring my Starlink, the other my TELUS connection.
  
### Tag Options
The Ookla speedtest app provides a nice set of data beyond the upload and download speed. The list is below.

| Tag Name 	| Description 	|
|-	|-	|
| isp 	| Your connections ISP 	|
| interface 	| Your devices connection interface 	|
| internal_ip 	| Your container or devices IP address 	|
| interface_mac 	| Mac address of your devices interface 	|
| vpn_enabled 	| Determines if VPN is enabled or not? I wasn't sure what this represented 	|
| external_ip 	| Your devices external IP address 	|
| server_id 	| The Speedtest ID of the server that  was used for testing 	|
| server_name 	| Name of the Speedtest server used  for testing 	|
| server_country 	| Country where the Speedtest server  resides 	|
| server_location | Location where the Speedtest server  resides  |
| server_host 	| Hostname of the Speedtest server 	|
| server_port 	| Port used by the Speedtest server 	|
| server_ip 	| Speedtest server's IP address 	|
| speedtest_id 	| ID of the speedtest results. Can be  used on their site to see results 	|
| speedtest_url 	| Link to the testing results. It provides your results as it would if you tested on their site.  	|

### Additional Notes
Be aware that this script will automatically accept the license and GDPR statement so that it can run non-interactively. Make sure you agree with them before running.

## Running the Script

### Docker Run 

1. Run the container.
    ```
     docker run -d -t --name speedflux \
    -e 'NAMESPACE'='None' \
    -e 'INFLUX_DB_ADDRESS'='influxdb' \
    -e 'INFLUX_DB_PORT'='8086' \
    -e 'INFLUX_DB_USER'='_influx_user_' \
    -e 'INFLUX_DB_PASSWORD'='_influx_pass_' \
    -e 'INFLUX_DB_DATABASE'='speedflux' \
    -e 'SPEEDTEST_INTERVAL'='5' \
    -e 'SPEEDTEST_FAIL_INTERVAL'='5'  \
    -e 'SPEEDTEST_SERVER_ID'='6601' \
    -e 'LOG_TYPE'='info' \
    dontobi/speedflux.rpi
    ```

## License
MIT License

Copyright (c) 2022 [Tobias 'dontobi' S.]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Credits
Inspired by [breadlysm](https://github.com/breadlysm/SpeedFlux) and [qlustor](https://github.com/qlustor/speedtest_ookla-to-influxdb)

This script looks to have been originally written by https://github.com/aidengilmartin/speedtest-to-influxdb/blob/master/main.py and I forked it from https://github.com/breadlysm/speedtest-to-influxdb. They did the hard work, I've continued to modify it though to fit my needs.

