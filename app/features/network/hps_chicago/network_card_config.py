import copy

from app.features.network.core.network_card_config import NetworkCardConfiguration as CoreNCC

class NetworkCardConfiguration(CoreNCC):
    """
    Network card configuration class for HPS-Chicago. Extends core network card config class.
    """

    def __init__(self):
        super().__init__()
        # Map to handle picking controls that have same text but different control IDs per card.
        self.alt_controls = { "Allowed for Voice Authorization": ["American Express", "Discover", "MasterCard", "Proprietary MasterCard", "Visa"],
                              "Preferred Track To Send To Host": ["FleetOne", "Fuelman", "GC/FleetWide"],
                              "Receipt Name": ["FleetOne", "Fuelman", "GC/FleetWide", "MasterCard Fleet", "MasterCard Purchase", "MFF PLCC Commercial", "MFF PLCC Consumer", 
                                               "MFF Visa", "Visa Fleet", "Visa Purchase", "Voyager", "WEX"] }

    def change(self, config):
        config = self._translate_map(config)
        return super().change(config)

    def _translate_map(self, map, card=None, _copy_map=True):
        """
        Certain fields in Chicago network card config Page 2 have varying control IDs depending on the selected card.
        Handle this in the background by recursively substituting the alternate control name into the user's map where necessary,
        so they don't have to worry about it.

        P.S. I hate this. -Cassidy

        Args:
            map: (dict) The settings map to translate.
            _copy_map: (bool) Whether to do a deep copy of the map before changing it, so as to not change the map
                             provided to the function. Used by this function to prevent redundant copying during recursion.
        Returns: (dict) The translated map.
        Example:
            >>> cfg = { "American Express": {"Page 2": { "Allowed for Voice Authorization": "Yes" }, "Page 3": { "Call Center Number": "12345" } },
                        "Fuelman": { "Page 1": {"Accept Card": "No"} },
                        "Proprietary DVM": { "Page 2": {"Receipt Name": "asdfsafd"} } }
            >>> translate_map(cfg)
            { "American Express": {"Page 2": { "Allowed for Voice Authorization 2": "Yes" }, "Page 3": { "Call Center Number": "12345" } },
            "Fuelman": { "Page 1": {"Accept Card": "No"} },
            "Proprietary DVM": { "Page 2": {"Receipt Name": "asdfsafd"} } }
        """
        if _copy_map:
            map = copy.deepcopy(map)
        for key, value in map.items():
            if card == None:
                card = key
            if key in self.alt_controls.keys() and card in self.alt_controls[key]:
                map.update({f"{key} 2": value})
                del map[key]
            elif type(value) is dict:
                self._translate_map(value, card, _copy_map=False)

        return map