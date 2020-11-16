import re
import json
from pathlib import Path
import random


name_map = {}
dices_pool = {}

def load_dices():
    global name_map
    global dices_pool
    dices_path = Path("./dices")
    total_count, failed_count = 0, 0
    for dices_file_path in dices_path.rglob("*.json"):
        with dices_file_path.open() as dices_file:
            print("正在解析"+str(dices_file_path)+"……")
            try:
                dices = json.loads(dices_file.read())
                for name, content in dices.items():
                    if "alias" in content:
                        alias = content.pop("alias")
                        if isinstance(alias, str):
                            name_map[alias] = name
                        if isinstance(alias, list):
                            for an_alias in alias:
                                name_map[an_alias] = name
                    name_map[name] = name
                    dices_pool[name] = content
            except JSONDecoderError:
                print("格式错误")
                failed_count = failed_count + 1
        total_count = total_count + 1
    print("共解析骰子配置文件 {0} 个，失败 {1} 个".format(total_count, failed_count))
    return

def debug_list_dices():
    for dicename, dicecontent in dices_pool.items():
        print(dicename+"="+str(dicecontent))
    return

def enumerated(dice: dict):
    def proc(matched: re.Match):
        # print(matched.group(0))
        returnStr = "["+matched.group(0)+"="
        count = 1 if matched.group("count")=="" else int(matched.group("count"))
        returnStr += str(random.choice(dice["content"]))
        for i in range(1, count):
            returnStr += ", " + str(random.choice(dice["content"]))
        returnStr += "]"
        # print(returnStr)
        return returnStr
    return proc

def ranged(dice: dict):
    def proc(matched: re.Match):
        # print(matched.group(0))
        returnStr = "["+matched.group(0)+"="
        count = 1 if matched.group("count")=="" else int(matched.group("count"))
        content = range(dice["range_low"], dice["range_high"]+1)
        returnStr += str(random.choice(content))
        for i in range(1, count):
            returnStr += ", " + str(random.choice(content))
        returnStr += "]"
        # print(returnStr)
        return returnStr
    return proc

def roll(a_dice: dict):
    if a_dice["type"] == "enumerated":
        closure = enumerated(a_dice)
        #return lambda x: enumerated(a_dice)(x)
    if a_dice["type"] == "ranged":
        closure = ranged(a_dice)
    # pending improvement
    return closure

def main():
    load_dices()
    print(str(sorted(name_map, key=lambda x: len(x), reverse=True)))
    while True:
        req = input(">>>")
        for replacement in sorted(name_map, key=lambda x: len(x), reverse=True):
            req = re.sub(r"(?<!\[)(?P<count>\d*)"+replacement, roll(dices_pool[name_map[replacement]]), req, flags=re.I)
        print(req)
    return

if __name__ == "__main__":
    main()