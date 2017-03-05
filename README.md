# CPSC 526 - Assignment 2
# Proxy Server in Python

Multi-client proxy server written in Python, with capabilities for output in various forms (hexdump, autoN(N sized blocks output on each line)

## Installation

Simply copy the ProxyServer.py file and run in from a terminal

## Usage

Call via "python3 ProxyServer.py [logoptions] sourcePort server destPort"
  - logoptions:
    - -raw Simply print out all data as assumed ASCII
    - -strip Strip and only output printable ASCII characters (Needs work)
    - -hex Output in the same style as linux hexdump (Needs work)
    - -autoN Data divided into N byte chunks, replace N with an integer value

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
