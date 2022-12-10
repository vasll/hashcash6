# Hashcash6

<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://i.imgur.com/wFKTpJk.png" alt="Logo" width="208.5" height="119.25">
  </a>
  
  <h3 align="center">Hashcash6</h3>
  
  <p align="center">
    A simple hashcash implementation that uses SHA3 384bit 
    <br />
    <a href="https://hashcash6.vasll.repl.co/"><strong>Try the web version here »</strong></a>
    <br />
    <br />
    <a href="https://github.com/vasll/Hashcash6/issues">Report Bug</a>
    ·
    <a href="https://github.com/vasll/Hashcash6/issues">Request Feature</a>
  </p>
  
  <br>
</div>

  ## Standalone script usage ##
  ```powershell 
  > python hashcash6.py [RESOURCE] [options]
  ```

  ### Sample command and output ###
  ```
  > python hashcash6.py sample@mail.com --zero-bits 22

Generating Hashcash6 for resource "sample@mail.com" with 22 zero bits using 1 thread... Done!

====================== Hashcash header =======================
X-Hashcash: 6:22:20221210104330.335636:sample@mail.com:LCwBlZTAIIw421mR:poFE

====================== Hexadecimal hash ======================
000000a19bb14d398ceb507d0abda9ca2490aa0424f1dbe185cdf0a53fc2c696facaeddca2293fceaf60d0c835fc103b

======================== Binary hash =========================
00000000000000000000000010100001100110111011000101001101001110011000110011101011010100000111...

Completed in 0:00:06.512355
```

