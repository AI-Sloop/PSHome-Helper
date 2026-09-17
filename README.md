# PSHome Helper

A small Linux helper for PlayStation Home (Destination Home) on RPCS3 — a floating, always-on-top toolbar that sits at the top of the screen and opens popups for **Who is Online**, **Shop**, and **Rewards**.

Built with Linux in mind — mainly Linux Mint, and SteamOS if you are in desktop mode.

This project is NOT affiliated with Destination Home, YourPSHome or PlayStation. The script runs **outside** RPCS3 — start it first, then launch Home in the emulator.

---

## What the buttons open

| Button | Site |
|---|---|
| Who is Online / Shop | [destinationhome.online](https://destinationhome.online/) |
| Rewards | [stores.yourpshome.net](https://stores.yourpshome.net/) |

---

## Requirements

- A Linux desktop session (Mint, or SteamOS **desktop mode**)
- Python 3
- [RPCS3](https://rpcs3.net/)
- The PlayStation Home package

Destination Home’s own setup guide is the right place to start:

[Getting started with Destination Home](https://destinationhome.online/docs/en/getting-started)

---

## Run it

```bash
python3 "PSHome Helper.py"
```

## Or mark it executable and run it directly:
```
chmod +x PSHome-Helper.py
./PSHome-Helper.py
```
