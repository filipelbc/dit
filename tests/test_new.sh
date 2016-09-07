
ditdir='./ditdir'

rm -rf $ditdir

./ditcmd new foo -d test

./ditcmd new bar/foo -d test

./ditcmd new zuu/abu/faa -d test

./ditcmd new /zoo -d test

./ditcmd new /bee/bii -d test

./ditcmd new goo//brr -d test

./ditcmd new //taa -d test

tree $ditdir

./ditcmd list "."

./ditcmd list "goo"

./ditcmd list "goo/."
