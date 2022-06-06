import json
from pathlib import Path
from typing import Dict, Set, NamedTuple, List

from BaseClasses import Item

TUNIC_ITEM_ID_OFFSET = 5000

TUNIC_PROGRESSION_ITEMS = [
    ""
]


class ItemData(NamedTuple):
    name: str
    code: int
    item_type: str
    progression: bool


class TunicItems:
    _item_table: List[ItemData] = []
    _item_table_lookup: Dict[str, ItemData] = {}

    def _populate_item_table_from_data(self):
        base_path = Path(__file__).parent
        file_path = (base_path / "data/ItemLocations.json").resolve()
        with open(file_path) as file:
            exported_items = json.load(file)
            self._item_table = []
            self._item_table_lookup = {}

            for tunic_item in exported_items:
                item_code = len(self._item_table) + TUNIC_ITEM_ID_OFFSET
                # Normal items
                if "itemName" in tunic_item and tunic_item["itemName"] not in self._item_table_lookup.keys():
                    new_item_name = f"{tunic_item['itemName']} x {max(tunic_item['itemQuantity'], 1)} " \
                                    f"[{item_code}]"
                    new_item = ItemData(new_item_name, item_code, tunic_item["itemType"],
                                        tunic_item["itemName"] in TUNIC_PROGRESSION_ITEMS)
                # Special items like Money and Empty Chests
                if "itemType" in tunic_item:
                    if tunic_item["itemType"] == "MONEY":
                        new_item_name = f"{max(tunic_item['moneyQuantity'], 1)}$ [{item_code}]"
                        new_item = ItemData(new_item_name, item_code, tunic_item["itemType"],
                                            False)
                    elif tunic_item["itemType"] == "OTHER":  # FOR NOW IT IS ONLY EMPTY CHESTS
                        new_item_name = f"Empty [{item_code}]"
                        new_item = ItemData(new_item_name, item_code, tunic_item["itemType"], False)

                # Add item
                self._item_table.append(new_item)
                self._item_table_lookup[new_item_name] = new_item

    def _get_item_table(self) -> List[ItemData]:
        if not self._item_table or not self._item_table_lookup:
            self._populate_item_table_from_data()
        return self._item_table

    def _get_item_table_lookup(self) -> Dict[str, ItemData]:
        if not self._item_table or not self._item_table_lookup:
            self._populate_item_table_from_data()
        return self._item_table_lookup

    def get_item_names_per_category(self) -> Dict[str, Set[str]]:
        categories: Dict[str, Set[str]] = {}

        for item in self._get_item_table():
            categories.setdefault(item.item_type, set()).add(item.name)

        return categories

    def generate_item(self, name: str, player: int) -> Item:
        item = self._get_item_table_lookup().get(name)
        return TunicItemWrapper(name, item.progression, item.code, player)

    def get_item_name_to_code_dict(self) -> Dict[str, int]:
        return {name: item.code for name, item in self._get_item_table_lookup().items()}

    def get_item(self, name: str) -> ItemData:
        return self._get_item_table_lookup()[name]

    def get_all_item_names(self) -> [str]:
        if not self._item_table or not self._item_table_lookup:
            self._populate_item_table_from_data()
        return [value.name for value in self._item_table]


class TunicItemWrapper(Item):
    game: str = "Tunic"
