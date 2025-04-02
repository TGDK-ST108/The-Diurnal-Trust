echo '<above payload>' | openssl enc -aes-256-cbc -a -salt -pass pass:QQUAp > EnzoQR.qr
qrencode -o Enzo_QSM_Badge.png < EnzoQR.qr