# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, time, datetime, random, string, shutil, ipaddress, subprocess, concurrent.futures Modules
import os, sys, time, datetime, random, string, shutil, ipaddress, subprocess, concurrent.futures
from N2G import drawio_diagram



# Devices access information (NETMIKO)
R1 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.1", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R2 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.2", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R3 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.3", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R4 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.4", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R5 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.5", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R6 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.6", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R7 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.7", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R8 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.8", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R9 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.9", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R10 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.10", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R11 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.11", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R12 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.12", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R13 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.13", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R14 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.14", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}



# Devices to be configured
HOSTS = [R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14]



# Paths
DIAGRAMS_PATH = "/home/pantelis/GNS3/projects/AUTOMATION/003_topology_diagrams/Diagrams/"



# Topology description
L3_TOPOLOGY_SEGMENTS = []
L3_TOPOLOGY = []
L2_TOPOLOGY_SEGMENTS = []
L2_TOPOLOGY = []



# Styles (SVG)
router = "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHN0eWxlPSJmaWxsLXJ1bGU6ZXZlbm9kZDtjbGlwLXJ1bGU6ZXZlbm9kZDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW1pdGVybGltaXQ6MiIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGhlaWdodD0iNjAiIHdpZHRoPSI2MCI+JiN4YTsgICAgPGNpcmNsZSBzdHlsZT0iZmlsbDojZmZmZWZlIiByPSIxNTAiIGN5PSIxNTAiIGN4PSIxNTAiLz4mI3hhOyAgICA8cGF0aCBzdHlsZT0iZmlsbDojMmQ2N2I5IiBkPSJNMTUwIDBjODIuNzg3IDAgMTUwIDY3LjIxMyAxNTAgMTUwcy02Ny4yMTMgMTUwLTE1MCAxNTBTMCAyMzIuNzg3IDAgMTUwIDY3LjIxMyAwIDE1MCAwWm0wIDE2YzczLjk1NyAwIDEzNCA2MC4wNDMgMTM0IDEzNHMtNjAuMDQzIDEzNC0xMzQgMTM0UzE2IDIyMy45NTcgMTYgMTUwIDc2LjA0MyAxNiAxNTAgMTZaIi8+JiN4YTsgICAgPHBhdGggdHJhbnNmb3JtPSJtYXRyaXgoLjg1MjAyIDAgMCAuODUyMDIgNDEuNTgxIDQxLjQ5MykiIHN0eWxlPSJmaWxsOiMyZDY3YjkiIGQ9Ik0xMzguNDU4IDE1Mi4yNzN2NDkuOTk2bDIwLjQ1Ny0yMC40NTUtLjA2OSAzMS4zNjYtMzEuNSAzMS41LTMxLjQzNC0zMS40MzV2LTMxLjQ3NmwyMC41MTggMjAuNTE4di00OS44NzJsMjIuMDI4LS4xNDJabTU2LjAzMy0zNS44NDNoNDkuODczbC4xNDEgMjIuMDI4aC00OS45OTZsMjAuNDU1IDIwLjQ1Ny0zMS4zNjUtLjA2OS0zMS41LTMxLjUgMzEuNDM0LTMxLjQzNGgzMS40NzZsLTIwLjUxOCAyMC41MThaTTcwLjk2NyAxNTguOTE1SDM5LjQ5bDIwLjUxOS0yMC41MThIMTAuMTM2bC0uMTQyLTIyLjAyOEg1OS45OUwzOS41MzYgOTUuOTEybDMxLjM2NS4wNjkgMzEuNSAzMS41LTMxLjQzNCAzMS40MzRabTQ1LjQwMi01Ni40ODFWNTIuNDM4TDk1LjkxMiA3Mi44OTNsLjA2OS0zMS4zNjYgMzEuNS0zMS40OTkgMzEuNDM0IDMxLjQzNHYzMS40NzZMMTM4LjM5NyA1Mi40MnY0OS44NzJsLTIyLjAyOC4xNDJaIi8+JiN4YTs8L3N2Zz4=;"
switch_multilayer = "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHN0eWxlPSJmaWxsLXJ1bGU6ZXZlbm9kZDtjbGlwLXJ1bGU6ZXZlbm9kZDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW1pdGVybGltaXQ6MiIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGhlaWdodD0iNjAiIHdpZHRoPSI2MCI+JiN4YTsgICAgPGNpcmNsZSBzdHlsZT0iZmlsbDojZmZmZWZlIiByPSIxNTAiIGN5PSIxNTAiIGN4PSIxNTAiLz4mI3hhOyAgICA8cGF0aCBzdHlsZT0iZmlsbDojMmQ2N2I5IiBkPSJNMTUwIDBjODIuNzg3IDAgMTUwIDY3LjIxMyAxNTAgMTUwcy02Ny4yMTMgMTUwLTE1MCAxNTBTMCAyMzIuNzg3IDAgMTUwIDY3LjIxMyAwIDE1MCAwWm0wIDE2YzczLjk1NyAwIDEzNCA2MC4wNDMgMTM0IDEzNHMtNjAuMDQzIDEzNC0xMzQgMTM0UzE2IDIyMy45NTcgMTYgMTUwIDc2LjA0MyAxNiAxNTAgMTZaIi8+JiN4YTsgICAgPHBhdGggdHJhbnNmb3JtPSJtYXRyaXgoLjk4MTQgMCAwIC45ODE0IDIuNzg5IDIuNzg5KSIgc3R5bGU9ImZpbGw6IzJkNjdiOSIgZD0iTTE0Mi4yMyAxMDAuNjQ3VjYyLjU3MWwtMTQuNDMgMTQuNDNWNTQuNjk1bDIyLjItMjIuMiAyMi4yIDIyLjJ2MjIuMzU0TDE1Ny44MDEgNjIuNjV2MzguMDAyYTQ5LjcwMSA0OS43MDEgMCAwIDEgMjEuNTk0IDguOTY0bDI2LjkzMy0yNi45MzJoLTIwLjQwN2wxNS43NzItMTUuNzcyaDMxLjM5NXYzMS4zOTVsLTE1LjgwNiAxNS44MDZWOTMuNzVsLTI2Ljg4IDI2Ljg4YTQ5LjcwNCA0OS43MDQgMCAwIDEgOC45NTEgMjEuNmgzOC4wNzZsLTE0LjQzLTE0LjQzaDIyLjMwNmwyMi4yIDIyLjItMjIuMiAyMi4yaC0yMi4zNTRsMTQuMzk5LTE0LjM5OWgtMzguMDAyYTQ5LjcwMSA0OS43MDEgMCAwIDEtOC45NjQgMjEuNTk0bDI2LjkzMiAyNi45MzN2LTIwLjQwN2wxNS43NzIgMTUuNzcydjMxLjM5NWgtMzEuMzk1bC0xNS44MDYtMTUuODA2aDIwLjM2M2wtMjYuODgtMjYuODhhNDkuNzA0IDQ5LjcwNCAwIDAgMS0yMS42IDguOTUxdjM4LjA3NmwxNC40My0xNC40M3YyMi4zMDZsLTIyLjIgMjIuMi0yMi4yLTIyLjJ2LTIyLjM1NGwxNC4zOTkgMTQuMzk5di0zOC4wMDJhNDkuNzAxIDQ5LjcwMSAwIDAgMS0yMS41OTQtOC45NjRsLTI2LjkzMyAyNi45MzJoMjAuNDA3bC0xNS43NzIgMTUuNzcySDY2LjkxMnYtMzEuMzk1bDE1LjgwNi0xNS44MDZ2MjAuMzYzbDI2Ljg4LTI2Ljg4YTQ5LjcwNCA0OS43MDQgMCAwIDEtOC45NTEtMjEuNkg2Mi41NzFsMTQuNDMgMTQuNDNINTQuNjk1bC0yMi4yLTIyLjIgMjIuMi0yMi4yaDIyLjM1NEw2Mi42NSAxNDIuMTk5aDM4LjAwMmE0OS43MDEgNDkuNzAxIDAgMCAxIDguOTY0LTIxLjU5NEw4Mi42ODQgOTMuNjcydjIwLjQwN0w2Ni45MTIgOTguMzA3VjY2LjkxMmgzMS4zOTVsMTUuODA2IDE1LjgwNkg5My43NWwyNi44OCAyNi44OGE0OS43MDQgNDkuNzA0IDAgMCAxIDIxLjYtOC45NTFabTcuNzcgMjAuMTQyYzE2LjEyMiAwIDI5LjIxMSAxMy4wODkgMjkuMjExIDI5LjIxMVMxNjYuMTIyIDE3OS4yMTEgMTUwIDE3OS4yMTEgMTIwLjc4OSAxNjYuMTIyIDEyMC43ODkgMTUwczEzLjA4OS0yOS4yMTEgMjkuMjExLTI5LjIxMVoiLz4mI3hhOzwvc3ZnPg==;"
switch = "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHN0eWxlPSJmaWxsLXJ1bGU6ZXZlbm9kZDtjbGlwLXJ1bGU6ZXZlbm9kZDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW1pdGVybGltaXQ6MiIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGhlaWdodD0iNjAiIHdpZHRoPSI2MCI+JiN4YTsgICAgPGNpcmNsZSBzdHlsZT0iZmlsbDojZmZmZWZlIiByPSIxNTAiIGN5PSIxNTAiIGN4PSIxNTAiLz4mI3hhOyAgICA8cGF0aCBzdHlsZT0iZmlsbDojMmQ2N2I5IiBkPSJNMTUwIDBjODIuNzg3IDAgMTUwIDY3LjIxMyAxNTAgMTUwcy02Ny4yMTMgMTUwLTE1MCAxNTBTMCAyMzIuNzg3IDAgMTUwIDY3LjIxMyAwIDE1MCAwWm0wIDE2YzczLjk1NyAwIDEzNCA2MC4wNDMgMTM0IDEzNHMtNjAuMDQzIDEzNC0xMzQgMTM0UzE2IDIyMy45NTcgMTYgMTUwIDc2LjA0MyAxNiAxNTAgMTZaIi8+JiN4YTsgICAgPHBhdGggdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTExLjY4IC0xMS42OCkgc2NhbGUoMS4wNzc4NykiIHN0eWxlPSJmaWxsOiMyZDY3YjkiIGQ9Ik05Ni41NzkgMTIxLjMxOUgxNTB2MjAuMzQ2SDk2LjY4NWwxOC45MTIgMTguOTEyaC0yOS4yOWwtMjkuMDk2LTI5LjA5NiAyOS4wOTYtMjkuMDk2aDI5LjIwNmwtMTguOTM0IDE4LjkzNFoiLz4mI3hhOyAgICA8cGF0aCB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMTEuNjggNjIuMTg4KSBzY2FsZSgxLjA3Nzg3KSIgc3R5bGU9ImZpbGw6IzJkNjdiOSIgZD0iTTk2LjU3OSAxMjEuMzE5SDE1MHYyMC4zNDZIOTYuNjg1bDE4LjkxMiAxOC45MTJoLTI5LjI5bC0yOS4wOTYtMjkuMDk2IDI5LjA5Ni0yOS4wOTZoMjkuMjA2bC0xOC45MzQgMTguOTM0WiIvPiYjeGE7ICAgIDxwYXRoIHRyYW5zZm9ybT0ibWF0cml4KC0xLjA3Nzg3IDAgMCAxLjA3Nzg3IDMxMS42OCAyOC4yMikiIHN0eWxlPSJmaWxsOiMyZDY3YjkiIGQ9Ik05Ni41NzkgMTIxLjMxOUgxNTB2MjAuMzQ2SDk2LjY4NWwxOC45MTIgMTguOTEyaC0yOS4yOWwtMjkuMDk2LTI5LjA5NiAyOS4wOTYtMjkuMDk2aDI5LjIwNmwtMTguOTM0IDE4LjkzNFoiLz4mI3hhOyAgICA8cGF0aCB0cmFuc2Zvcm09Im1hdHJpeCgtMS4wNzc4NyAwIDAgMS4wNzc4NyAzMTEuNjggLTQ1LjY0NykiIHN0eWxlPSJmaWxsOiMyZDY3YjkiIGQ9Ik05Ni41NzkgMTIxLjMxOUgxNTB2MjAuMzQ2SDk2LjY4NWwxOC45MTIgMTguOTEyaC0yOS4yOWwtMjkuMDk2LTI5LjA5NiAyOS4wOTYtMjkuMDk2aDI5LjIwNmwtMTguOTM0IDE4LjkzNFoiLz4mI3hhOzwvc3ZnPg==;"
hub = "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHN0eWxlPSJmaWxsLXJ1bGU6ZXZlbm9kZDtjbGlwLXJ1bGU6ZXZlbm9kZDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW1pdGVybGltaXQ6MiIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGhlaWdodD0iNjAiIHdpZHRoPSI2MCI+JiN4YTsgICAgPGNpcmNsZSBzdHlsZT0iZmlsbDojZmZmZWZlIiByPSIxNTAiIGN5PSIxNTAiIGN4PSIxNTAiLz4mI3hhOyAgICA8cGF0aCBzdHlsZT0iZmlsbDojMmQ2N2I5IiBkPSJNMTUwIDBjODIuNzg3IDAgMTUwIDY3LjIxMyAxNTAgMTUwcy02Ny4yMTMgMTUwLTE1MCAxNTBTMCAyMzIuNzg3IDAgMTUwIDY3LjIxMyAwIDE1MCAwWm0wIDE2YzczLjk1NyAwIDEzNCA2MC4wNDMgMTM0IDEzNHMtNjAuMDQzIDEzNC0xMzQgMTM0UzE2IDIyMy45NTcgMTYgMTUwIDc2LjA0MyAxNiAxNTAgMTZaIi8+JiN4YTsgICAgPHBhdGggdHJhbnNmb3JtPSJtYXRyaXgoMCAtMS40NzE5OSAxLjcxMjExIDAgLTIyOC44ODQgMjE1LjA1OCkiIHN0eWxlPSJmaWxsOiMyZDY3YjkiIGQ9Ik01MS4zNTIgMTcxLjQ4N3Y3Ni44MzhjMCAxLjk0MyAxNC4zNzgtMTIuNTA5IDE0LjM3OC0xMS4yOHYxNy4xNGMwIDEuMjc4LTE5LjAwNyAxNi42MDYtMjEuNDk3IDE2LjkxNXYuMDA1bC0uMDM1LS4wMDItLjAzNi4wMDJ2LS4wMDVjLTIuNDktLjMwOS0yMS40OTctMTUuNjM3LTIxLjQ5Ny0xNi45MTV2LTE3LjE0YzAtMS4yMjkgMTQuMzc5IDEzLjIyMyAxNC4zNzkgMTEuMjh2LTc2LjgzOGgxNC4zMDhaIi8+JiN4YTs8L3N2Zz4=;"
link = "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHN0eWxlPSJmaWxsLXJ1bGU6ZXZlbm9kZDtjbGlwLXJ1bGU6ZXZlbm9kZDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW1pdGVybGltaXQ6MiIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGhlaWdodD0iNjAiIHdpZHRoPSI2MCI+JiN4YTsgICAgPGNpcmNsZSBzdHlsZT0iZmlsbDojZmZmZWZlIiByPSIxNTAiIGN5PSIxNTAiIGN4PSIxNTAiLz4mI3hhOyAgICA8cGF0aCBzdHlsZT0iZmlsbDojZTMxYzAwIiBkPSJNMTUwIDBjODIuNzg3IDAgMTUwIDY3LjIxMyAxNTAgMTUwcy02Ny4yMTMgMTUwLTE1MCAxNTBTMCAyMzIuNzg3IDAgMTUwIDY3LjIxMyAwIDE1MCAwWm0wIDE2YzczLjk1NyAwIDEzNCA2MC4wNDMgMTM0IDEzNHMtNjAuMDQzIDEzNC0xMzQgMTM0UzE2IDIyMy45NTcgMTYgMTUwIDc2LjA0MyAxNiAxNTAgMTZaIi8+JiN4YTsgICAgPHBhdGggdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTEuOTMgMTEuOTYpIHNjYWxlKC45MjA0NykiIHN0eWxlPSJmaWxsOiNlMzFjMDAiIGQ9Im0xNDAuNzggMTUwLjk2NCA5LjgwOC05LjgwOS01Ljc2Ny01Ljc2OGMtNS41NjYtNS41NjUtNS41NjYtMTQuNjAyIDAtMjAuMTY3bDUxLjg0Mi01MS44NDJjNS41NjUtNS41NjUgMTQuNjAyLTUuNTY1IDIwLjE2NyAwbDIwLjE2NyAyMC4xNjdjNS41NjYgNS41NjYgNS41NjYgMTQuNjAyIDAgMjAuMTY3bC01MS44NDIgNTEuODQzYy01LjU2NSA1LjU2NS0xNC42MDIgNS41NjUtMjAuMTY3IDBsLTUuNzY4LTUuNzY4LTkuODA4IDkuODA4IDUuNzY3IDUuNzY4YzUuNTY2IDUuNTY2IDUuNTY2IDE0LjYwMiAwIDIwLjE2N2wtNTEuODQyIDUxLjg0M2MtNS41NjUgNS41NjUtMTQuNjAyIDUuNTY1LTIwLjE2NyAwbC0yMC4xNjctMjAuMTY4Yy01LjU2Ni01LjU2NS01LjU2Ni0xNC42MDIgMC0yMC4xNjdsNTEuODQyLTUxLjg0MmM1LjU2NS01LjU2NSAxNC42MDItNS41NjUgMjAuMTY3IDBsNS43NjggNS43NjhabS0xMi4xNiAxMi4xNmE1LjIzNyA1LjIzNyAwIDAgMC02LjczMy41NjRsLTQwLjMxMSA0MC4zMTFhNS4yMzUgNS4yMzUgMCAwIDAgMCA3LjRsNy40IDcuNGE1LjIzNSA1LjIzNSAwIDAgMCA3LjQgMGw0MC4zMTEtNDAuMzExYTUuMjM3IDUuMjM3IDAgMCAwIC41NjUtNi43MzNsLTMuNDQgMy40NGE0LjI2NyA0LjI2NyAwIDAgMS02LjAzMSAwbC0yLjYwMS0yLjYwMWE0LjI2NyA0LjI2NyAwIDAgMSAwLTYuMDMxbDMuNDQtMy40MzlabTQyLjg0MS0yNS41NzhhNS4yMzYgNS4yMzYgMCAwIDAgNi43MzMtLjU2NWw0MC4zMTEtNDAuMzExYTUuMjM1IDUuMjM1IDAgMCAwIDAtNy40bC03LjQtNy40YTUuMjM1IDUuMjM1IDAgMCAwLTcuNCAwbC00MC4zMTEgNDAuMzExYTUuMjM4IDUuMjM4IDAgMCAwLS41NjUgNi43MzNsMy40MjQtMy40MjRhNC4yNjcgNC4yNjcgMCAwIDEgNi4wMzEgMGwyLjYwMSAyLjYwMWE0LjI2NyA0LjI2NyAwIDAgMSAwIDYuMDMxbC0zLjQyNCAzLjQyNFoiLz4mI3hhOzwvc3ZnPg==;"



def l3_node(INPUT_DICT_PER_HOST):
    global L3_TOPOLOGY_SEGMENTS

    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds node hostname.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]

    # Sends execution commands.
    exec_output_1 = net_connect.send_command("show ip interface | include Internet address | line protocol")
    exec_output_2 = net_connect.send_command("show arp")

    # Creates temporary files (if the specified files do not exist) and overwrites any existing content (if there are).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output_1, file=f)
    with open("arp" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output_2, file=f)

    # Finds node interface-address pairs.
    L3_INTERFACE_ADDRESS_PAIRS = []
    with open("interfaces_temporary" + random_string, "r") as file:
        previous_line = ""
        for line in file:
            if "Internet address" in line:
                L3_INTERFACE_ADDRESS_PAIRS.append([previous_line.split()[0], line.split()[3]])
            else:
                pass
            previous_line = line

    # Finds node ARP table.
    L3_ARP = []
    with open("arp" + random_string, "r") as file:
        for line in file:
            if line.split()[1] != "Address" and line.split()[5] != "Ethernet0/0":
                L3_ARP.append([line.split()[5], line.split()[1], line.split()[2]])
            else:
                pass

    # Deletes the temporary files.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)
    else:
        pass
    if os.path.exists("arp" + random_string):
        os.remove("arp" + random_string)
    else:
        pass

    # Finds node segments.
    L3_NODE_SEGMENTS = []
    for element in L3_ARP:
        if element[2] == "-":
            X = []
            Y = set()
            Y.clear()
            X.append(HOST_HOSTNAME)
            X.append(element[0])
            for item in L3_INTERFACE_ADDRESS_PAIRS:
                if element[0] == item[0] and element[1] == item[1].split("/")[0]:
                    X.append(ipaddress.ip_network(item[1], strict=False).with_prefixlen)
                else:
                    pass
            for item in L3_ARP:
                if element[0] == item[0]:
                    Z = item[1].split(".")[3]
                    Z = "R" + Z
                    Y.add(Z)
                else:
                    pass
            X.append(Y)
            L3_NODE_SEGMENTS.append(X)
        else:
            pass

    # Discovers topology segments.
    L3_TOPOLOGY_SEGMENTS = L3_TOPOLOGY_SEGMENTS + L3_NODE_SEGMENTS

    # Disconnects from host.
    net_connect.disconnect()

    # Prints all level 3 segments for the node.
    print(L3_NODE_SEGMENTS)



def l3_diagram(INPUT_LIST_FOR_TOPOLOGY):
    global L3_TOPOLOGY

    # Discovers topology.
    for element in INPUT_LIST_FOR_TOPOLOGY:
        L3_LIST = []
        for item in INPUT_LIST_FOR_TOPOLOGY:
            if element[2] == item[2] and element[3] == item[3]:
                if item not in L3_LIST:
                    L3_LIST.append(item)
                else:
                    pass
            else:
                pass
        if len(L3_LIST) == 2:
            X = {"source": {"id": L3_LIST[0][0], "label": L3_LIST[0][0], "style": router}, "src_label": L3_LIST[0][1], "label": L3_LIST[0][2], "target": {"id": L3_LIST[1][0], "label": L3_LIST[1][0], "style": router}, "trgt_label": L3_LIST[1][1]}
            L3_TOPOLOGY.append(X)
        else:
            X = []
            for element in L3_LIST:
                Y = {"source": {"id": element[0], "label": element[0], "style": router}, "src_label": element[1], "label": element[2], "target": {"id": "MULTI_ACCESS " + element[2], "label": "MULTI_ACCESS " + element[2], "style": link}, "trgt_label": ""}
                X.append(Y)
            L3_TOPOLOGY = L3_TOPOLOGY + X

    # Prints all level 3 segments for the topology.
    print(L3_TOPOLOGY)

    # Draw topology.
    diagram = drawio_diagram()
    diagram.from_list(L3_TOPOLOGY, width=400, height=400, diagram_name="l3_diagram")
    diagram.layout(algo="kk")
    diagram.dump_file(filename="l3_diagram.drawio", folder=DIAGRAMS_PATH)



def l2_node(INPUT_DICT_PER_HOST):
    global L2_TOPOLOGY_SEGMENTS

    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds node hostname.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]

    # Sends execution commands.
    exec_output = net_connect.send_command("show cdp neighbors")

    # Creates temporary files (if the specified files do not exist) and overwrites any existing content (if there are).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("cdp" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds node CDP table.
    L2_CDP = []
    COUNT_LINES = 0
    EMPTY_LINE_TRACK = 0
    with open("cdp" + random_string, "r") as file:
        for line in file:
            COUNT_LINES = COUNT_LINES + 1
            if len(line.strip()) == 0:
                EMPTY_LINE_TRACK = EMPTY_LINE_TRACK + 1
            else:
                pass
            if COUNT_LINES > 5 and EMPTY_LINE_TRACK < 2:
                L2_CDP.append([HOST_HOSTNAME, line.split()[1] + line.split()[2], line.split()[0].split(".")[0]])
            else:
                pass

    # Deletes the temporary files.
    if os.path.exists("cdp" + random_string):
        os.remove("cdp" + random_string)
    else:
        pass

    # Removes management interface.
    L2_CDP_FILTERED = []
    for element in L2_CDP:
        if element[1] != "Eth0/0":
            L2_CDP_FILTERED.append(element)
        else:
            pass

    # Finds node segments.
    TRACK = []
    L2_NODE_SEGMENTS = []
    for element in L2_CDP_FILTERED:
        X =[]
        Y = set()
        Y.clear()
        if element[1] not in TRACK:
            TRACK.append(element[1])
            X.append(element[0])
            X.append(element[1])
            for item in L2_CDP_FILTERED:
                if element[1] == item[1]:
                    Y.add(item[2])
                else:
                    pass
            X.append(Y)
            L2_NODE_SEGMENTS.append(X)
        else:
            pass

    # Discovers topology segments.
    L2_TOPOLOGY_SEGMENTS = L2_TOPOLOGY_SEGMENTS + L2_NODE_SEGMENTS

    # Disconnects from host.
    net_connect.disconnect()

    # Prints all level 2 segments for the node.
    print(L2_NODE_SEGMENTS)



def l2_diagram(INPUT_LIST_FOR_TOPOLOGY):
    global L2_TOPOLOGY

    # Assigns ID to links.
    L2_TOPOLOGY_SEGMENTS_WITH_ID = []
    for element in INPUT_LIST_FOR_TOPOLOGY:
        X = []
        LINK_ID = set()
        LINK_ID.clear()
        LINK_ID.update(element[2])
        LINK_ID.update({element[0]})
        X.append(element[0])
        X.append(element[1])
        X.append(LINK_ID)
        X.append(element[2])
        L2_TOPOLOGY_SEGMENTS_WITH_ID.append(X)

    # Discovers topology.
    TRACK = []
    for element in L2_TOPOLOGY_SEGMENTS_WITH_ID:
        L2_LIST = []
        if element[2] not in TRACK:
            TRACK.append(element[2])
            for item in L2_TOPOLOGY_SEGMENTS_WITH_ID:
                if element[2] == item[2]:
                    L2_LIST.append(item)
                else:
                    pass
        else:
            pass
        if len(L2_LIST) == 2:
            X = {"source": {"id": L2_LIST[0][0], "label": L2_LIST[0][0], "style": router}, "src_label": L2_LIST[0][1], "target": {"id": L2_LIST[1][0], "label": L2_LIST[1][0], "style": router}, "trgt_label": L2_LIST[1][1]}
            L2_TOPOLOGY.append(X)
        else:
            X = []
            RANDOM_STRING = ''.join(random.choices(string.ascii_letters, k=10))
            for element in L2_LIST:
                Y = {"source": {"id": element[0], "label": element[0], "style": router}, "src_label": element[1], "target": {"id": RANDOM_STRING, "label": "MULTI_ACCESS", "style": link}, "trgt_label": ""}
                X.append(Y)
            L2_TOPOLOGY = L2_TOPOLOGY + X


    # Prints all level 3 segments for the topology.
    print(L2_TOPOLOGY)

    # Draw topology.
    diagram = drawio_diagram()
    diagram.from_list(L2_TOPOLOGY, width=400, height=400, diagram_name="l2_diagram")
    diagram.layout(algo="kk")
    diagram.dump_file(filename="l2_diagram.drawio", folder=DIAGRAMS_PATH)



# CODE!!!



# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.
print("\033[1;91m")
print()
print()
print()
print("The LEVEL-3 segments, per node, are as following:")
print()
print()
print()
print("\033[0m")
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(l3_node, element) for element in HOSTS]

print("\033[1;91m")
print()
print()
print()
print("The LEVEL-3 diagram description is as following:")
print()
print()
print()
print("\033[0m")
l3_diagram(L3_TOPOLOGY_SEGMENTS)

print("\033[1;91m")
print()
print()
print()
print("The LEVEL-2 segments, per node, are as following:")
print()
print()
print()
print("\033[0m")
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(l2_node, element) for element in HOSTS]

print("\033[1;91m")
print()
print()
print()
print("The LEVEL-2 diagram description is as following:")
print()
print()
print()
print("\033[0m")
l2_diagram(L2_TOPOLOGY_SEGMENTS)
