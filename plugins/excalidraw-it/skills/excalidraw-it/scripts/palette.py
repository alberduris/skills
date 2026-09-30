"""The open-color shades the pieces draw with: 1 fills, 6 and 7 draw borders and titles, 9 writes on a shade 1 fill."""
OPEN_COLOR = {
    "gray": {1: "#f1f3f5", 6: "#868e96", 7: "#495057", 9: "#212529"},
    "red": {1: "#ffe3e3", 6: "#fa5252", 7: "#f03e3e", 9: "#c92a2a"},
    "pink": {1: "#ffdeeb", 6: "#e64980", 7: "#d6336c", 9: "#a61e4d"},
    "grape": {1: "#f3d9fa", 6: "#be4bdb", 7: "#ae3ec9", 9: "#862e9c"},
    "violet": {1: "#e5dbff", 6: "#7950f2", 7: "#7048e8", 9: "#5f3dc4"},
    "indigo": {1: "#dbe4ff", 6: "#4c6ef5", 7: "#4263eb", 9: "#364fc7"},
    "blue": {1: "#d0ebff", 6: "#228be6", 7: "#1c7ed6", 9: "#1864ab"},
    "cyan": {1: "#c5f6fa", 6: "#15aabf", 7: "#1098ad", 9: "#0b7285"},
    "teal": {1: "#c3fae8", 6: "#12b886", 7: "#0ca678", 9: "#087f5b"},
    "green": {1: "#d3f9d8", 6: "#40c057", 7: "#37b24d", 9: "#2b8a3e"},
    "lime": {1: "#e9fac8", 6: "#82c91e", 7: "#74b816", 9: "#5c940d"},
    "yellow": {1: "#fff3bf", 6: "#fab005", 7: "#f59f00", 9: "#e67700"},
    "orange": {1: "#ffe8cc", 6: "#fd7e14", 7: "#f76707", 9: "#d9480f"},
}


def shade(name, level):
    return OPEN_COLOR[name][level]
