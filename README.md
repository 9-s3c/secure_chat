# secure_chat
socket messaging program that implements single use RSA 4096 and fernet for secure communication

when a connection is established, both the client and server generate a RSA 4096 key pair and exchange public keys with eachother. the server then generates a fernet (AES256) symetric key and sends it to the client using the clients public key. after that its pretty much just a regular socket chat, i threw this together in a few hours so i could talk with a friend who didnt trust any of the common "encrypted" communication apps. didnt think id put it on github, but everything is private rn just logging what i do for the future. there is a python file and a linux binary
