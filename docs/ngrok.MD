# NGROK How To

## Link to NGROK tool

* https://dashboard.ngrok.com/get-started/your-authtoken

## Linux

* https://download.ngrok.com/linux
* `ngrok config add-authtoken <MY_AUTHTOKEN>`
* `ngrok http 59001 --host-header="localhost:59001"`

## Windows

* https://download.ngrok.com/windows?tab=download
* `./ngrok.exe config add-authtoken <MY_AUTHTOKEN>`
* `./ngrok.exe http 59001 --host-header="localhost:59001"`
