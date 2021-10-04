#!/usr/bin/env python3
from builtins import str, dict, list

CRA = "\u030a"  # Combining Ring Above - used to mark potential indeterminate pronunciations


def char_range(c1, c2):
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


syl2latin_dict:dict = dict()
syl2latin_vowels:list = ["a" + CRA, "e" + CRA, "i" + CRA, "o" + CRA, "u" + CRA, "v" + CRA]

for syl, latin in zip(char_range("Ꭰ", "Ꭵ"), syl2latin_vowels):
    syl2latin_dict[syl] = latin

syl2latin_dict["Ꭶ"] = "ga" + CRA
syl2latin_dict["Ꭷ"] = "ka" + CRA

for syl, latin in zip(char_range("Ꭸ", "Ꭼ"), syl2latin_vowels[1:]):
    syl2latin_dict[syl] = "g" + CRA + latin
    
for syl, latin in zip(char_range("Ꭽ", "Ꮂ"), syl2latin_vowels):
    syl2latin_dict[syl] = "h" + latin
    
for syl, latin in zip(char_range("Ꮃ", "Ꮈ"), syl2latin_vowels):
    syl2latin_dict[syl] = "l" + latin
    
for syl, latin in zip(char_range("Ꮉ", "Ꮍ"), syl2latin_vowels[:-1]):
    syl2latin_dict[syl] = "m" + latin
    
syl2latin_dict["Ꮎ"] = "na" + CRA
syl2latin_dict["Ꮐ"] = "na" + CRA + "h"
syl2latin_dict["Ꮏ"] = "hna" + CRA

for syl, latin in zip(char_range("Ꮑ", "Ꮕ"), syl2latin_vowels[1:]):
    syl2latin_dict[syl] = "h" + CRA + "n" + latin
    
for syl, latin in zip(char_range("Ꮖ", "Ꮛ"), syl2latin_vowels):
    syl2latin_dict[syl] = "g" + CRA + "w" + latin
    
syl2latin_dict["Ꮜ"] = "sa" + CRA
syl2latin_dict["Ꮝ"] = "s"

for syl, latin in zip(char_range("Ꮞ", "Ꮢ"), syl2latin_vowels[1:]):
    syl2latin_dict[syl] = "s" + latin

syl2latin_dict["Ꮣ"] = "da" + CRA
syl2latin_dict["Ꮤ"] = "ta" + CRA
syl2latin_dict["Ꮥ"] = "de" + CRA
syl2latin_dict["Ꮦ"] = "te" + CRA
syl2latin_dict["Ꮧ"] = "di" + CRA
syl2latin_dict["Ꮨ"] = "ti" + CRA
syl2latin_dict["Ꮩ"] = "d" + CRA + "o" + CRA
syl2latin_dict["Ꮪ"] = "d" + CRA + "u" + CRA
syl2latin_dict["Ꮫ"] = "d" + CRA + "v" + CRA

syl2latin_dict["Ꮬ"] = "dla" + CRA
syl2latin_dict["Ꮭ"] = "tla" + CRA

for syl, latin in zip(char_range("Ꮮ", "Ꮲ"), syl2latin_vowels[1:]):
    syl2latin_dict[syl] = "d" + CRA + "l" + latin
    
for syl, latin in zip(char_range("Ꮳ", "Ꮸ"), syl2latin_vowels):
    syl2latin_dict[syl] = "j" + CRA + latin
    
for syl, latin in zip(char_range("Ꮹ", "Ꮾ"), syl2latin_vowels):
    syl2latin_dict[syl] = "h" + CRA + "w" + latin
    
for syl, latin in zip(char_range("Ꮿ", "Ᏼ"), syl2latin_vowels):
    syl2latin_dict[syl] = "h" + CRA + "y" + latin

    
def syl2latin(text:str) -> str:
    latin = ""
    for c in text:
        if c in syl2latin_dict:
            latin += syl2latin_dict[c]
        else:
            latin += c
    return latin


def test():
    print(syl2latin("ᎣᏏᏲ, ᏙᎯᏧ? ᏙᎯᏊ."))
    
    cedTest = [ "U²sgal²sdi ạ²dv¹ne²³li⁴sgi.",
                "Ụ²wo²³dị³ge⁴ɂi gi²hli a¹ke²³he³²ga na ạ²chu⁴ja.",
                "Ạ²ni²³tạɂ³li ạ²ni²sgạ²ya a¹ni²no²hạ²li²³do³²he, ạ²hwi du¹ni²hyọ²he.",
                "Sa¹gwu⁴hno ạ²sgạ²ya gạ²lo¹gwe³ ga²ne²he sọ³ɂị³hnv³ hla².",
                "Na³hnv³ gạ²lo¹gwe³ ga²ne⁴hi u²dlv²³kwsạ²ti ge¹se³, ạ²le go²hu⁴sdi yu²³dv³²ne⁴la a¹dlv²³kwsge³.",
                "A¹na³ɂi²sv⁴hnv go²hu⁴sdi wu²³ni³go²he do²jụ²wạ³ɂị²hlv,",
                "na³hnv³ gạ²lo¹gwe³ ga²ne⁴hi kị²lạ²gwu ị²yv⁴da wị²du²³sdạ³yo²hle³ o²³sdạ²gwu nu²³ksẹ²stạ²nv⁴na ị²yu³sdi da¹sdạ²yo²hị²hv⁴.",
                "U²do²hị²yu⁴hnv³ wu²³yo³hle³ ạ²le u¹ni²go²he³ gạ²nv³gv⁴.",
                "Na³hnv³ gạ²lo¹gwe³ nị²ga²³ne³hv⁴na \"ạ²hwi e¹ni²yo³ɂa!\" u¹dv²hne.",
                "\"Ji²yo³ɂe³²ga\" u¹dv²hne na³ gạ²lo¹gwe³ ga²ne⁴hi, a¹dlv²³kwsgv³.",
                "U¹na³ne²lu²³gi³²se do²jụ²wạ³ɂị²hlv³ di³dla, nạ²ɂv²³hnị³ge⁴hnv wu²³ni³luh²ja u¹ni²go²he³ so²³gwị³li gạɂ³nv⁴.",
                "\"So²³gwị³lị³le³² i¹nạ²da²hị³si\" u¹dv²hne³ na³ u²yo²hlv⁴.", "\"Hạ²da²hị³se³²ga³\" a¹go¹se²³le³." ]
    
    for a in cedTest:
        print("_______________");
        print();
        print(a);
        print(ced2mco(a));
        
    asciiCedText = ["ga.2da.2de3ga", "ha.2da.2du1ga", "u2da.2di23nv32di", "u1da.2di23nv32sv23?i", "a1da.2de3go3?i"]
    for a in asciiCedText:
        print("_______________");
        print();
        print(a);
        print(ascii_ced2mco(a));
    return 


# Converts MCO annotation into pseudo English phonetics for use by the aeneas alignment package
# lines prefixed with '#' are returned with the '#' removed, but otherwise unchanged.
def mco2espeak(text:str):
    import unicodedata as ud
    import re
    
    if (len(text.strip()) == 0):
        return ""
    
    # Handle specially flagged text
    if (text[0].strip() == "#"):
        if text[1] != "!":
            return text.strip()[1:]
        else:
            text = text[2:]
    
    newText = ud.normalize('NFD', text.strip()).lower()
    if (newText[0] == ""):
        newText = newText[1:]
        
    # remove all tone indicators
    newText = re.sub("[\u030C\u0302\u0300\u0301\u030b]", "", newText)
    newText = "[[" + newText.strip() + "]]"
    newText = newText.replace(" ", "]] [[")
    newText = newText.replace("'", "]]'[[")
    newText = newText.replace(".]]", "]].")
    newText = newText.replace(",]]", "]],")
    newText = newText.replace("!]]", "]]!")
    newText = newText.replace("?]]", "]]?")
    newText = newText.replace(":]]", "]]:")
    newText = newText.replace(";]]", "]];")
    newText = newText.replace("\"]]", "]]\"")
    newText = newText.replace("']]", "]]'")
    newText = newText.replace(" ]]", "]] ")
    newText = newText.replace("[[ ", " [[")
    newText = re.sub("(?i)([aeiouv]):", "\\1", newText)
    # convert all vowels into approximate espeak x-sampa escaped forms
    newText = newText.replace("A", "0")
    newText = newText.replace("a", "0")
    newText = newText.replace("v", "V")
    newText = newText.replace("tl", "tl#")
    newText = newText.replace("hl", "l#")
    newText = newText.replace("J", "dZ")
    newText = newText.replace("j", "dZ")
    newText = newText.replace("Y", "j")
    newText = newText.replace("y", "j")
    newText = newText.replace("Ch", "tS")
    newText = newText.replace("ch", "tS")
    newText = newText.replace("ɂ", "?")
    
    return newText

    
def ced2mco(text:str):
    import unicodedata as ud
    import re

    tones2mco = [("²³", "\u030C"), ("³²", "\u0302"), ("¹", "\u0300"), ("²", ""), ("³", "\u0301"), ("⁴", "\u030b")]
    
    text = ud.normalize('NFD', text)
    text = re.sub("(?i)([aeiouv])([^¹²³⁴\u0323]+)", "\\1\u0323\\2", text)
    text = re.sub("(?i)([aeiouv])([¹²³⁴]+)$", "\\1\u0323\\2", text)
    text = re.sub("(?i)([aeiouv])([¹²³⁴]+)([^¹²³⁴a-zɂ])", "\\1\u0323\\2\\3", text)
    text = re.sub("(?i)([^aeiouv\u0323¹²³⁴]+)([¹²³⁴]+)", "\\2\\1", text)
    text = re.sub("(?i)([aeiouv])([¹²³⁴]+)", "\\1\\2:", text)
    text = text.replace("\u0323", "")
    text = re.sub("(?i)([aeiouv])²$", "\\1\u0304", text)
    text = re.sub("(?i)([aeiouv])²([^a-zɂ¹²³⁴:])", "\\1\u0304\\2", text)
    for ced2mcotone in tones2mco:
        text = text.replace(ced2mcotone[0], ced2mcotone[1])
    #
    return ud.normalize('NFC', text)


def ascii_ced2mco(text:str):
    import unicodedata as ud
    text = ud.normalize('NFD', text)
    text = text.replace(".", "\u0323")
    text = text.replace("1", "¹")
    text = text.replace("2", "²")
    text = text.replace("3", "³")
    text = text.replace("4", "⁴")
    text = text.replace("?", "ɂ")
    return ced2mco(text)


if __name__ == "__main__":
    test()
