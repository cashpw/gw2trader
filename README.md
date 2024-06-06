# Guild Wars 2 Trader

Know before you trade!

```sh
$ python3 main.py
                       item_name                            gw2bltc_url        roi%  buy_stacks buy_price buy_stack_price total_buy_price sell_price sell_stack_price invest_cum_sum
0            Bag of Coffee Beans  https://www.gw2bltc.com/en/item/82991  101.307898         3.0        6c         15s  0c         45s  0c        13c          32s 50c        45s  0c
1               Dragonfish Candy  https://www.gw2bltc.com/en/item/43363   45.569042         7.0       94c      2g 35s  0c     16g 45s  0c     1s 20c       3g  0s  0c    16g 90s  0c
2            Kralkachocolate Bar  https://www.gw2bltc.com/en/item/43358   40.893278         4.0       92c      2g 30s  0c      9g 20s  0c     1s 19c       2g 97s 50c    26g 10s  0c
3      Glass of Buttered Spirits  https://www.gw2bltc.com/en/item/77667   34.278881         4.0        9c         22s 50c         90s  0c        15c          37s 50c    27g  0s  0c
4                       Koi Cake  https://www.gw2bltc.com/en/item/43361   32.675970        26.0       97c      2g 42s 50c     63g  5s  0c     1s 56c       3g 90s  0c    90g  5s  0c
5                Soft Wood Plank  https://www.gw2bltc.com/en/item/19713   31.855850         7.0       47c      1g 17s 50c      8g 22s 50c        70c       1g 75s  0c    98g 27s 50c
6                  Soft Wood Log  https://www.gw2bltc.com/en/item/19726   27.603633        23.0       19c         47s 50c     10g 92s 50c        28c          70s  0c   109g 20s  0c
7      Cup of Spiced Apple Cider  https://www.gw2bltc.com/en/item/77648   27.221863         3.0        9c         22s 50c         67s 50c        14c          35s  0c   109g 87s 50c
8   Slice of Candied Dragon Roll  https://www.gw2bltc.com/en/item/43362   25.307917         4.0       94c      2g 35s  0c      9g 40s  0c     1s 46c       3g 65s  0c   119g 27s 50c
9              Seasoned Wood Log  https://www.gw2bltc.com/en/item/19727   22.665519        21.0       54c      1g 35s  0c     28g 35s  0c        76c       1g 90s  0c   147g 62s 50c
...
```

## Setup

1. (Optional) Create and enter a virtual environment

    ```sh
    python -m venv .venv
    source ./venv/bin/activate
    ```
1. Install [https://github.com/cashpw/gw2tpdb](`gw2tpdb`)

    ```sh
    python3 -m pip install git+https://github.com/cashpw/gw2tpdb.git~
    ```

### Local development

I install a local version of [https://github.com/cashpw/gw2tpdb](`gw2tpdb`) to develop both in sync:

``` sh
python3 -m pip install -e ~/proj/gw2tpdb
```

## Usage

``` sh
python3 main.py
```

## Roadmap

- Quality
    - Tidy the code
    - Split `main.py` into separate files
- Features
    - Provide more context and documentation in flipping reports
    - Allow command-line customization
    - Detect trends (e.g. annual rise/fall or weekday-vs-weekend rise/fall)
