# -*- coding:utf-8 -*-
"""
Date         : 2026-01-30
Author       : cuihx
Requirements : python==3.11.9
"""
import json
from collections import namedtuple
# from cuihx import cuihx_logging
class cuihx_logging:

    @staticmethod
    def info(mes):
        print(f"\033[92m{mes}\033[0m")

    @staticmethod
    def warning(mes):
        print(f"\033[93m{mes}\033[0m")

    @staticmethod
    def debug(mes):
        print(f"\033[94m{mes}\033[0m")


place_calculate_tuple = namedtuple('place_calculate', ["地点", "基础属性", "副属性"])

class Weapon:
    def __init__(self):
        with open("data/基础.json", "r", encoding='utf-8') as _f:
            self.base_data = json.loads(_f.read())
        _all_key = self.base_data["基础"] + self.base_data["附加"] + self.base_data["技能"]
        if len(_all_key) != len(set(_all_key)):
            cuihx_logging.warning("三大基础属性有重复，如果是版本更新请调整check函数")
        with open("data/武器.json", "r", encoding='utf-8') as _f:
            self.weapon_data = json.loads(_f.read())
        with open("data/能量淤积点.json", "r", encoding='utf-8') as _f:
            self.place_data = json.loads(_f.read())
        for _place_name, _place_data in self.place_data.items():
            for _key in ["基础", "附加", "技能"]:
                for _value in _place_data[_key]:
                    if _value not in self.base_data[_key]:
                        cuihx_logging.warning(f"[{_place_name}][{_key}]属性异常->{_value}")
                        raise
        for _weapon_name, _weapon in self.weapon_data.items():
            for _key in ["基础", "附加", "技能"]:
                if _weapon[_key] not in self.base_data[_key] and not (_key == "附加" and _weapon[_key] == "-"):
                    cuihx_logging.warning(f"[{_weapon_name}][{_key}]属性异常->{_weapon[_key]}")
                    raise

    def calculate(self, weapon, level=3):
        _weapon_info = self.weapon_data.get(weapon)
        if not _weapon_info:
            cuihx_logging.warning(f"缺失武器->{weapon}")
            return
        for _place_name, _place_data in self.place_data.items():
            if not(_weapon_info["基础"] in _place_data["基础"] and (_weapon_info["附加"] in _place_data["附加"] or _weapon_info["附加"] == "-") and _weapon_info["技能"] in _place_data["技能"]):
                continue  # 此武器无法在此副本毕业
            cuihx_logging.info(f'{"-" * 30}{_place_name}{"-" * 30}')
            if _weapon_info["附加"] != "-":
                print(f'{"-" * 20}基础:{_weapon_info["基础"]}--附加:{_weapon_info["附加"]}{"-" * 20}')
                _res = self.place_calculate(data=place_calculate_tuple(地点=_place_name, 基础属性=_weapon_info["基础"], 副属性=_weapon_info["附加"]), level=level)
                for _other_key in _res.keys():
                    if not _res[_other_key]:
                        continue
                    print(_other_key)
                    for _value in _res[_other_key]:
                        print(f"\t{_value}")
            print(f'{"-" * 20}基础:{_weapon_info["基础"]}--技能:{_weapon_info["技能"]}{"-" * 20}')
            _res = self.place_calculate(data=place_calculate_tuple(地点=_place_name, 基础属性=_weapon_info["基础"], 副属性=_weapon_info["技能"]), level=level)
            for _other_key in _res.keys():
                if not _res[_other_key]:
                    continue
                print(_other_key)
                for _value in _res[_other_key]:
                    print(f"\t{_value}")

    def place_calculate(self, data: place_calculate_tuple, level):
        if data.地点 not in self.place_data.keys():
            cuihx_logging.warning("地点不存在")
            return None
        _place_data = self.place_data[data.地点]
        if data.基础属性 not in _place_data["基础"]:
            cuihx_logging.warning(f"武器无法在此副本毕业-主属性异常")
            return None
        _return_dict = {_key: set() for _key in _place_data["基础"] if _key != data.基础属性}
        if not(data.副属性 in _place_data["附加"] or data.副属性 in _place_data["技能"]):
            cuihx_logging.warning(f"武器无法在此副本毕业-副本属性异常")
            return None
        for _weapon, _weapon_data in self.weapon_data.items():
            if int(_weapon_data["星级"]) < level:
                continue
            if _weapon_data["基础"] == data.基础属性 or _weapon_data["基础"] not in _return_dict:
                continue
            if data.副属性 in _place_data["附加"] and data.副属性 == _weapon_data["附加"] and _weapon_data["技能"] in _place_data["技能"]:
                _return_dict[_weapon_data["基础"]].add((_weapon, *_weapon_data.values()))
            elif data.副属性 in _place_data["技能"] and data.副属性 == _weapon_data["技能"] and (_weapon_data["附加"] in _place_data["附加"] or _weapon_data["附加"] == "-"):
                _return_dict[_weapon_data["基础"]].add((_weapon, *_weapon_data.values()))
        return _return_dict
    
    def check(self, data: tuple[str, str, str], mes = None):
        if mes is None:
            mes = ""
        _input = {}
        if "主能力提升" in data and "强攻" in data:
            cuihx_logging.info(f"可使[3星武器]毕业->{mes}")
        for _value in data:
            for _key in ["基础", "附加", "技能"]:
                if _value in self.base_data[_key]:
                    _input[_key] = _value
                    break
            else:
                cuihx_logging.warning(f"不在基础属性中，请检查输入->{mes}")
                return
        if len(_input) < 3:
            cuihx_logging.debug(f"暂无武器可毕业,是不是没用刻写券->{mes}")
            return
        _is_find = False
        for _weapon_name, _weapon_info in self.weapon_data.items():
            if _input["基础"] == _weapon_info["基础"] and _input["附加"] == _weapon_info["附加"] and _input["技能"] == _weapon_info["技能"]:
                cuihx_logging.info(f"可使{_weapon_name}毕业->{mes}")
                _is_find = True
        if not _is_find:
            cuihx_logging.debug(f"暂无武器可毕业->{mes}")



if __name__ == '__main__':
    root = Weapon()
    root.calculate("宏愿")
    # root.check(("物理伤害提升", "敏捷提升", "迸发"))
