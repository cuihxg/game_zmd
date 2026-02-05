# -*- coding:utf-8 -*-
"""
Date         : 2026-01-30
Author       : cuihx
Requirements : python==3.11.9
"""
import json
from collections import namedtuple


class P:

    @staticmethod
    def green(mes):
        print(f"\033[92m{mes}\033[0m")

    @staticmethod
    def yellow(mes):
        print(f"\033[93m{mes}\033[0m")

    @staticmethod
    def blue(mes):
        print(f"\033[94m{mes}\033[0m")

    @staticmethod
    def grey(mes):
        print(f"\033[90m{mes}\033[0m")


place_calculate_tuple = namedtuple('place_calculate_tuple', ["地点", "基础属性", "副属性"])


class Weapon:
    def __init__(self):
        with open("data/基础.json", "r", encoding='utf-8') as _f:
            self.base_data = json.loads(_f.read())
        _all_key = self.base_data["基础"] + self.base_data["附加"] + self.base_data["技能"]
        if len(_all_key) != len(set(_all_key)):
            P.yellow("三大基础属性有重复，如果是版本更新请调整check函数")
        with open("data/武器.json", "r", encoding='utf-8') as _f:
            self.weapon_data = json.loads(_f.read())
        with open("data/能量淤积点.json", "r", encoding='utf-8') as _f:
            self.place_data = json.loads(_f.read())
        for _place_name, _place_data in self.place_data.items():
            for _key in ["基础", "附加", "技能"]:
                for _value in _place_data[_key]:
                    if _value not in self.base_data[_key]:
                        P.yellow(f"[{_place_name}][{_key}]属性异常->{_value}")
                        raise
        for _weapon_name, _weapon in self.weapon_data.items():
            for _key in ["基础", "附加", "技能"]:
                if _weapon[_key] not in self.base_data[_key] and not (_key == "附加" and _weapon[_key] == "-"):
                    P.yellow(f"[{_weapon_name}][{_key}]属性异常->{_weapon[_key]}")
                    raise

    def calculate(self, weapon, level=3, *, _sort_index = 1):
        """
        :param weapon: 武器名称
        :param level: 筛选武器星级
        :param _sort_index: 0为总出货率排序，1为已获取未毕业出货率
        :return:
        """
        _all_place_probability = []  # 存放各副本的推荐值
        _weapon_info = self.weapon_data.get(weapon)
        if not _weapon_info:
            P.yellow(f"缺失武器->{weapon}")
            return
        P.green(f"{weapon}---{list(_weapon_info.values())}")
        for _place_name, _place_data in self.place_data.items():
            if not (_weapon_info["基础"] in _place_data["基础"] and (_weapon_info["附加"] in _place_data["附加"] or _weapon_info["附加"] == "-") and _weapon_info["技能"] in _place_data["技能"]):
                continue  # 此武器无法在此副本毕业
            _place_probability = []  # 存放当前副本的推荐值
            P.green(f"├─{_place_name}")
            for _calculate_attribute, _other_attribute in [("附加", "技能"), ("技能", "附加")]:
                if _calculate_attribute == "附加" and _weapon_info[_calculate_attribute] == "-":
                    continue
                _attribute_probability = {}  # 存放当前选择的概率
                print(f'│   ├─{_calculate_attribute}:{_weapon_info[_calculate_attribute]}')
                _res = self.place_calculate(data=place_calculate_tuple(地点=_place_name, 基础属性=_weapon_info["基础"], 副属性=_weapon_info[_calculate_attribute]), level=level)
                _all_count = len(_place_data[_other_attribute])
                for _basic_attribute in _res.keys():
                    if not _res[_basic_attribute]:
                        continue
                    _this_count = {"总": set(), "已获取未毕业": set()}
                    print(f"│   │   ├─{_basic_attribute}" if _weapon_info["基础"] != _basic_attribute else f"│   │   ├─{_basic_attribute}[必选]")
                    for _value in _res[_basic_attribute]:
                        if '未获取' in _value or '已毕业' in _value:
                            if _weapon_info["基础"] != _basic_attribute:
                                P.grey(f"│   │   │   ├─{_value}")
                            if self.weapon_data[_value[0]][_other_attribute] in self.place_data[_place_name][_other_attribute]:
                                _this_count["总"].add(self.weapon_data[_value[0]][_other_attribute])
                        else:
                            if _weapon_info["基础"] != _basic_attribute:
                                P.blue(f"│   │   │   ├─{_value}")
                            if self.weapon_data[_value[0]][_other_attribute] in self.place_data[_place_name][_other_attribute]:
                                _this_count["总"].add(self.weapon_data[_value[0]][_other_attribute])
                                _this_count["已获取未毕业"].add(self.weapon_data[_value[0]][_other_attribute])
                    _attribute_probability[_basic_attribute] = (round(len(_this_count['总']) / _all_count * 100, 2),
                                                                          round(len(_this_count['已获取未毕业']) / _all_count * 100, 2))
                    print(f"│   │   │   └──总出货率 {_attribute_probability[_basic_attribute][0]} %\t已获取未毕业出货率 {_attribute_probability[_basic_attribute][1]} %")
                if len(_attribute_probability) < 3:
                    _probability = [0, 0]
                    for _value in _attribute_probability.values():
                        _probability[0] += _value[0] / 3
                        _probability[1] += _value[1] / 3
                    P.grey(f"│   │   └──{_weapon_info[_calculate_attribute]}--{'|'.join(_attribute_probability.keys())}|任意, "
                           f"总出货率 {round(_probability[0], 2)} %\t已获取未毕业出货率 {round(_probability[1], 2)} %")
                    _place_probability.append((f"{'|'.join(_attribute_probability.keys())}|任意|{_calculate_attribute}:{_weapon_info[_calculate_attribute]}", *_probability))
                else:
                    _sorted_items = sorted(_attribute_probability.items(), key=lambda x: x[_sort_index], reverse=True)
                    _basic_attributes = [_weapon_info["基础"]]
                    _probability = [_attribute_probability[_weapon_info["基础"]][0] / 3, _attribute_probability[_weapon_info["基础"]][1] / 3]
                    _basic_count = 0
                    for _key, _value in _sorted_items:
                        if _key == _weapon_info["基础"]:
                            continue
                        _basic_count += 1
                        if _basic_count > 2 :
                            break
                        _probability[0] += _value[0] / 3
                        _probability[1] += _value[1] / 3
                        _basic_attributes.append(_key)
                    _place_probability.append((f"{'|'.join(_basic_attributes)}|{_calculate_attribute}:{_weapon_info[_calculate_attribute]}", *_probability))
                    P.blue(f"│   │   └──推荐 {_weapon_info[_calculate_attribute]}--{'|'.join(_basic_attributes)}, 总出货率 {round(_probability[0], 2)} %\t已获取未毕业出货率 {round(_probability[1], 2)} %")
            _place_probability.sort(key=lambda x: x[_sort_index + 1], reverse=True)
            _all_place_probability.append((_place_name, *_place_probability[0]))
            P.green(f"│   └──推荐 {_place_probability[0][0]}, 总出货率 {round(_place_probability[0][1], 2)} %\t已获取未毕业出货率 {round(_place_probability[0][2], 2)} %")
        _all_place_probability.sort(key=lambda x: x[_sort_index + 2], reverse=True)
        P.green(f"└──推荐 {_all_place_probability[0][0]}--{_all_place_probability[0][1]}, 总出货率 {round(_all_place_probability[0][2], 2)} %\t已获取未毕业出货率 {round(_all_place_probability[0][3], 2)} %")


    def place_calculate(self, data: place_calculate_tuple, level):
        if data.地点 not in self.place_data.keys():
            P.yellow("地点不存在")
            return None
        _place_data = self.place_data[data.地点]
        if data.基础属性 not in _place_data["基础"]:
            P.yellow(f"武器无法在此副本毕业-主属性异常")
            return None
        _return_dict = {_key: set() for _key in _place_data["基础"]}
        if not (data.副属性 in _place_data["附加"] or data.副属性 in _place_data["技能"]):
            P.yellow(f"武器无法在此副本毕业-副本属性异常")
            return None
        for _weapon, _weapon_data in self.weapon_data.items():
            if int(_weapon_data["星级"]) < level:
                continue
            if _weapon_data["基础"] not in _return_dict:
                continue
            if _weapon_data["基础"] == data.基础属性:
                _return_dict[_weapon_data["基础"]].add((_weapon, *_weapon_data.values()))
            if data.副属性 in _place_data["附加"] and data.副属性 == _weapon_data["附加"] and _weapon_data["技能"] in \
                    _place_data["技能"]:
                _return_dict[_weapon_data["基础"]].add((_weapon, *_weapon_data.values()))
            elif data.副属性 in _place_data["技能"] and data.副属性 == _weapon_data["技能"] and (
                    _weapon_data["附加"] in _place_data["附加"] or _weapon_data["附加"] == "-"):
                _return_dict[_weapon_data["基础"]].add((_weapon, *_weapon_data.values()))
        return _return_dict

    def check(self, data: tuple[str, str, str], mes=None):
        if mes is None:
            mes = ""
        _input = {}
        if "主能力提升" in data and "强攻" in data:
            P.green(f"可使[3星武器]毕业->{mes}")
        for _value in data:
            for _key in ["基础", "附加", "技能"]:
                if _value in self.base_data[_key]:
                    _input[_key] = _value
                    break
            else:
                P.yellow(f"不在基础属性中，请检查输入->{mes}")
                return
        if len(_input) < 3:
            P.blue(f"暂无武器可毕业,是不是没用刻写券->{mes}")
            return
        _is_find = False
        for _weapon_name, _weapon_info in self.weapon_data.items():
            if _input["基础"] == _weapon_info["基础"] and _input["附加"] == _weapon_info["附加"] and _input["技能"] == _weapon_info["技能"]:
                P.green(f"可使 {_weapon_name} | {_weapon_info['类型']} | {_weapon_info['星级']} | {_weapon_info.get('状态')}  毕业->{mes}")
                _is_find = True
        if not _is_find:
            P.blue(f"暂无武器可毕业->{mes}")


if __name__ == '__main__':
    root = Weapon()
    root.calculate("宏愿")  # 推荐给 [武器.json] 加个属性[状态]，未获取/已毕业，方便计算出货率
    # root.check(("物理伤害提升", "敏捷提升", "迸发"))
