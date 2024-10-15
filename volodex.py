#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lzma
import json
import math
import click
import requests
import mtg_parser
import webbrowser

from tqdm import tqdm
from collections import Counter
from operator import itemgetter, attrgetter

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Static, Label, ListView, ListItem, RichLog


class CompositeLabelItem(ListItem):
    def __init__(self, label:str, quantity:int) -> None:
        super().__init__()
        self.label = label
        self.quantity = quantity

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f'{self.label}')
            yield Label(f'{self.quantity}', classes='right')


class CardListItem(ListItem):
    def __init__(self, card:dict) -> None:
        super().__init__()
        self.card = card
        self.key = card['name']

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.card['name'])
            yield Label(self.card['manaCost'], classes='right')


class CreatureApp(App):

    CSS_PATH = "volodex.css"
    BINDINGS = [
        ("q", "quit", "Quit Volodex"),
        ("a", "sort_alnum", "Toggle Sort Types"),
        ("c", "sort_cmc", "Toggle Sort CMCs"),
        ("v", "view_card", "View Card in Browser"),
    ]

    user_deck_list = reactive([])

    def __init__(self, volodex:list, decklist:str):
        super().__init__()

        self.title = 'Python Volodex'
        self.sub_title = decklist
        self.volodex = volodex

        self.sort_alnum = False
        self.sort_cmc = False

        self.type_list = ListView(
            id='type_list',
            classes='column w20',
        )
        self.creature_list = ListView(
            id='creature_list',
            classes='column w20',
        )
        self.creature_detail = Static(
            'Select a creature to view details.',
            id='creature_details',
            classes='column w40',
            disabled=True,
        )
        self.rich_log = RichLog(
            classes='h20',
            # disabled=True,
        )


    def action_quit(self) -> None:
        self.exit()


    async def action_sort_alnum(self) -> None:
        self.rich_log.write(f'action_sort_alnum()')
        self.sort_alnum = not self.sort_alnum
        self.rich_log.write(f'self.sort_alnum={self.sort_alnum}')
        await self.on_mount()


    async def action_sort_cmc(self) -> None:
        self.rich_log.write(f'action_sort_cmc()')
        self.sort_cmc = not self.sort_cmc
        self.rich_log.write(f'self.sort_cmc={self.sort_cmc}')
        event = ListView.Highlighted(self.type_list, self.type_list.highlighted_child)
        await self._on_type_highlighted(event)


    def action_view_card(self) -> None:
        item = self.creature_list.highlighted_child
        if item:
            card = item.card
            url = f"https://scryfall.com/search?&q={card['name']}"
            self.rich_log.write(url)
            webbrowser.open(url)


    def on_key(self, event) -> None:
        if event.key == 'tab':
            if self.focused is self.type_list:
                self.creature_list.focus()
            else:
                self.type_list.focus()


    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(classes='h80'):
            yield self.type_list
            yield self.creature_list
            yield self.creature_detail
        yield self.rich_log
        yield Footer()


    async def on_mount(self) -> None:
        self.rich_log.write(f'on_mount()')

        all_types = []
        for card in self.volodex:
            all_types.extend(card['subtypes'])
        all_types_dict = dict(Counter(all_types).most_common())

        items = (CompositeLabelItem(name, quantity) for name,quantity in all_types_dict.items())
        if self.sort_alnum:
            items = sorted(items, key=attrgetter('label'))
        await self.type_list.clear()
        await self.type_list.extend(items)
        self.type_list.index = 0


    @on(ListView.Highlighted, "#type_list")
    async def _on_type_highlighted(self, event:ListView.Highlighted) -> None:
        self.rich_log.write(f'_on_type_highlighted()')
        self.rich_log.write(event.item)

        await self.creature_list.clear()

        if event.item:
            selected_subtype = event.item.label
            cards = filter(lambda card: selected_subtype in card['subtypes'], self.volodex)

            if self.sort_cmc:
                cards = sorted(cards, key=itemgetter('manaValue'))
            else:
                cards = sorted(cards, key=itemgetter('edhrecRank'))

            items = (CardListItem(card) for card in cards)
            await self.creature_list.extend(items)
            self.creature_list.index = 0


    @on(ListView.Highlighted, "#creature_list")
    def _on_creature_highlighted(self, event:ListView.Highlighted) -> None:
        self.rich_log.write(f'_on_creature_highlighted()')
        self.rich_log.write(event.item)

        details = "No details available."

        if event.item:
            card_name = event.item.key
            card = next(card for card in self.volodex if card['name'] == card_name)
            details = '\n'.join([
                f"{card.get('name')} — {card.get('manaCost')}",
                "",
                card.get('type'),
                "",
                f"{card.get('power')}/{card.get('toughness')}",
                "",
                card.get('text'),
            ])

        self.creature_detail.update(details)


def load_volodex(filename:str, decklist:str) -> list:
    with open(filename, 'r', encoding='utf-8') as f:
        volodex = json.load(f)

    banned_types = set([ 'Human', 'Wizard', ])

    if decklist:
        decklist_card_names = set(card.name for card in mtg_parser.parse_deck(decklist))
        for card in volodex:
            if card['name'] in decklist_card_names:
                banned_types.update(card['subtypes'])

    return [card for card in volodex if not set(card['subtypes']) & banned_types]


@click.group()
def main():
    pass


@main.command()
@click.argument('decklist', type=str, required=False)
def run(decklist):
    """Launch the app with an optional decklist"""
    volodex = load_volodex('volodex.json', decklist)
    app = CreatureApp(volodex, decklist)
    app.run()


@main.command()
def download():
    """Download AtomicCards.json.xz from mtgjson"""
    url = 'https://mtgjson.com/api/v5/AtomicCards.json.xz'
    compressed_path = 'AtomicCards.json.xz'

    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))

    with open(compressed_path, 'wb') as f:
        with tqdm(total=total_size_in_bytes, unit='B', unit_scale=True, desc=f'Downloading {compressed_path}', ascii=True) as progress_bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))


@main.command()
def update():
    """Update or create volodex.json from AtomicCards.json.xz"""
    with lzma.open('AtomicCards.json.xz', 'rt') as f:
        atomic_cards = json.load(f)

    filtered_cards = []
    unique_card_names = set()

    for cards in tqdm(atomic_cards.get('data', {}).values(), desc="Updating volodex"):
        for card in cards:
            if card.get('legalities', {}).get('commander') != 'Legal':
                continue
            if 'Creature' not in card.get('type'):
                continue
            if card.get('isFunny'):
                continue
            color_identity = set(card.get('colorIdentity', []))
            if color_identity & set('WBR'):
                continue
            subtypes = card.get('subtypes', [])
            if 'Human' in subtypes or 'Wizard' in subtypes:
                continue
            card_name = card.get('faceName') or card.get('name')
            if card_name in unique_card_names:
                continue
            unique_card_names.add(card_name)
            filtered_cards.append({
                'name': card_name,
                'fullName': card.get('name'),
                'colorIdentity': ''.join(color_identity),
                'manaCost': card.get('manaCost', '/'),
                'manaValue': math.floor(card.get('manaValue', 0)),
                'type': card.get('type'),
                'subtypes': subtypes,
                'edhrecRank': card.get('edhrecRank', 999999),
                'text': card.get('text', ''),
                'power': card.get('power'),
                'toughness': card.get('toughness'),
            })

    with open('volodex.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_cards, f, indent=4)

    print('Total Cards', len(filtered_cards))


if __name__ == "__main__":
    main()
