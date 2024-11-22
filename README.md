# mtg-volodex

The `volodex` is a CLI companion app to discover new creatures for your [Volo, Guide to Monsters](https://scryfall.com/card/afr/238/volo-guide-to-monsters) Commander deck.
The application displays only the creature types that are not currently in your decklist, if one is provided.


## Table of contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Caching](#caching)


> [!CAUTION]
> This code was written specifically to solve my unique use case and workflow. It is designed to meet my requirements and priorities, and as such, it may not follow the most optimal practices or be universally applicable.
>
> If you find the code useful for your purposes, feel free to use or modify it as needed. However, I cannot guarantee its suitability for any use case other than my own. Use at your own discretion! 😊


## Prerequisites

Before using the `volodex`, you will need:
- `python >= 3.x`


## Dependencies

The `volodex` uses the following python packages:
- [click](https://pypi.org/project/click/)
- [more-itertools](https://pypi.org/project/more-itertools/)
- [requests](https://pypi.org/project/requests/)
- [mtg-parser](https://pypi.org/project/mtg_parser/)
- [textual](https://pypi.org/project/textual/)
- [tqdm](https://pypi.org/project/tqdm/)


You don't need to manually install them, this is done when executing `./install.sh`.

Cards database is fetched from the [mtgjson.com](https://mtgjson.com) api.


## Getting Started


### Install the app

Set the virtual environment and install the dependencies:

```Shell
$ ./install.sh
```


### Setup the card database

Download the card database and filter it:

```Shell
$ ./volodex.sh download
$ ./volodex.sh update
```

See also [Caching](#caching).


### Launch the application

Launch the cli `volodex` application:

```Shell
$ ./volodex.sh run [DECKLIST_URL]
```

If the `volodex` is launched with a decklist, creature types will be filtered to only show the ones that are not already included in the deck.

If the `volodex` is launched with no argument, all creatures elligible for a [Volo, Guide to Monsters](https://scryfall.com/card/afr/238/volo-guide-to-monsters) Commander deck will be listed.

The `volodex` relies on [mtg-parser](https://pypi.org/project/mtg_parser/) for parsing decklists and thus, supports the same deck building websites.


## Usage

🚧 WIP


## Caching

The `volodex` creates two local cache files.
- `./AtomicCards.json.xz` is fetched from [mtgjson.com](https://mtgjson.com) when running the `./volodex.sh download` command. This file contains the list of all mtg cards.
- `./volodex.json` is created/updated when running the `./volodex.sh update` command. This file only contains the relevant cards for a [Volo, Guide to Monsters](https://scryfall.com/card/afr/238/volo-guide-to-monsters) Commander deck.
