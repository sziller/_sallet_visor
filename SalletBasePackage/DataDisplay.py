def rec_dict_plotter(dictionary: dict, string= "", itemnumbering: bool = None, level: int = 0, switch=True, on=True):
    """ Function name: rec_dict_plotter =======================================================================
    Template: rdp as in (R)ecursive (D)ictionary (P)lotter
    This is a function to show a dictionary of any deepness in a tree structure.
    Keep it intact, only develop in general ways.
    :param dictionary:      the dictionary to be processed. Can be any level deep.
                            Values are distinguished btw. dict or non dict.
    :param itemnumbering:   way of numbering data:
                                True  - all items will be numbered
                                False - only keys having subdictionaries will be numbered
                                None  - no line will be numbered
    :param level:           a 'static' type counter. By default: 0. Can be modified if need to.
                            It is defined, in order to avoid the usage of global parameters.
    :param on: bool - if True, user will get important messages in the console at runtime.
    :param switch: bool - if True, developer will get messages in the console at runtime.
    :return: nothing as a template
    ============================================================================================== by Sziller ==="""
    if on and switch:
        for key, value in sorted(dictionary.items()):
            if isinstance(value, dict):
                line = {True:  level * "  " + '(%s) %s:' % (level, key),
                        False:  level * "  " + '(%s) %s:' % (level, key),
                        None: level * "    " + '%s:' % key}
                # print(line[itemnumbering])
                string += line[itemnumbering]
                string = rec_dict_plotter(value, string, itemnumbering, level + 1)
            else:
                line = {
                    False:   level * "  " + "    %s: %s" % (key, value),
                    True:   level * "  " + "(%s) %s: %s" % (level, key, value),
                    None:  level * "    " + "%s: %s" % (key, value)}
                # print(line[itemnumbering])
                string += line[itemnumbering]
        return string


def rec_list_plotter(list_in: list, string= "", itemnumbering: bool = None, level: int = 0):
    """ Function name: rec_list_plotter =================================================================
    Template: rdp as in (R)ecursive (D)ictionary (P)lotter
    This is a function to show a dictionary of any deepness in a tree structure.
    Keep it intact, only develop in general ways.
    :param list_in:      the list to be processed. Can be any level deep.
                            Values are distinguished btw. dict or non dict.
    :param itemnumbering:   way of numbering data:
                                True  - all items will be numbered
                                False - only lists having sublists will be numbered
                                None  - no line will be numbered
    :param level:           a 'static' type counter. By default: 0. Can be modified if need to.
                            It is defined, in order to avoid the usage of global parameters.
    :param on: bool - if True, user will get important messages in the console at runtime.
    :param switch: bool - if True, developer will get messages in the console at runtime.
    :return: nothing as a template
    ============================================================================================== by Sziller ==="""
    for item in list_in:
        if isinstance(item, list):
            line = {
                False:  level * "| " + ">",
                None:   level * "| " + ">",
                True:   level * "| " + '(%s): >' % level}
            # print(line[itemnumbering])
            string += line[itemnumbering]
            string = rec_list_plotter(item, string, itemnumbering, level + 1)
        else:
            line = {
                False:  level * "| " + "%s" % item,
                None:   level * "| " + "%s" % item,
                True:   level * "| " + "(%s)%s" % (level, item)}
            # print(line[itemnumbering])
            string += line[itemnumbering]
        return string


def rec_data_plotter(data, string= "", itemnumbering: bool = False, level: int = 0, switch=True, on=True):
    """ Function name: rec_data_plotter =================================================================
    Template: rdap as in (R)ecursive (DA)ta (P)lotter
    This is a function to show a dictionary of any deepness in a tree structure.
    Keep it intact, only develop in general ways.
    :param data:      the list to be processed. Can be any level deep.
                            Values are distinguished btw. dict or non dict.
    :param itemnumbering:   way of numbering data:
                                True  - all items will be numbered
                                False - only lists having sublists will be numbered
                                None  - no line will be numbered
    :param level:           a 'static' type counter. By default: 0. Can be modified if need to.
                            It is defined, in order to avoid the usage of global parameters.
    :param on: bool - if True, user will get important messages in the console at runtime.
    :param switch: bool - if True, developer will get messages in the console at runtime.
    :return: nothing as a template
    ============================================================================================== by Sziller ==="""

    if isinstance(data, list):
        for item in data:
            if isinstance(item, list):
                line = {
                    False:                      level * "|   " + "[...] list\n",
                    True: '(%s)  ' % level +    level * "|   " + "[...] list\n"}
                # string += line[itemnumbering]
                string = rec_data_plotter(item, string, itemnumbering, level + 1)

            elif isinstance(item, dict):
                line = {
                    False:                      level * "|   " + "{...} dict\n",
                    True: '(%s)  ' % level +    level * "|   " + "{...} dict\n"}
                # string += line[itemnumbering]
                string = rec_data_plotter(item, string, itemnumbering, level + 1)
            else:
                line = {
                    False:                      level * "|   " + "%s\n" % item,
                    True: '(%s)  ' % level +    level * "|   " + "%s\n" % item}
                string += line[itemnumbering]

        return string

    elif isinstance(data, dict):
        for key, value in sorted(data.items()):
            if isinstance(value, dict):
                line = {
                    False:                      level * "|   " + '%s: ' % key + "{...} dict\n",
                    True: '(%s)  ' % level +    level * "|   " + '%s: ' % key + "{...} dict\n"}
                string += line[itemnumbering]
                string = rec_data_plotter(value, string, itemnumbering, level + 1)
            elif isinstance(value, list):
                line = {
                    False:                      level * "|   " + '%s: ' % key + "[...] list\n",
                    True: '(%s)  ' % level +    level * "|   " + '%s: ' % key + "[...] list\n"}
                string += line[itemnumbering]
                string = rec_data_plotter(value, string, itemnumbering, level + 1)
            else:
                line = {
                    False:                      level * "|   " + "%s: %s\n" % (key, value),
                    True: '(%s)  ' % level +    level * "|   " + "%s: %s\n" % (key, value)}
                string += line[itemnumbering]
        return string
    else:
        line = {
            False:                      level * "|   " + ">>> %s\n" % data,
            True: "(%s)  " % level +    level * "|   " + ">>> %s\n" % data}
        string += line[itemnumbering]
        return string


if __name__  == "__main__":
    statedict = {
        "screen_status": {
            "seq": 0,
            'inst': 'button_nav_status',
            'down': ['button_nav_status'],
            'normal': ["button_nav_settings", "button_nav_control"]},
        "screen_settings": {
            "seq": 1,
            'inst': 'button_nav_settings',
            'down': ['button_nav_settings'],
            'normal': ["button_nav_status", "button_nav_control"]},
        "screen_control": {
            "seq": 2,
            'inst': 'button_nav_control',
            'down': ['button_nav_control'],
            'normal': ["button_nav_status", "button_nav_settings"]}
    }

    a = rec_data_plotter(data=statedict, string="")
    print(a)
