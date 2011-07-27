import re

class ExecutableInformation:
    def __init__(self,
                 filename):

        define_re = '#define ([a-zA-Z0-9_\(\)]*) ([a-zA-Z0-9_\(\)]*).*'
        define_re_c = re.compile(define_re)
        value_re = '\(([0-9]*)L\)'
        value_re_c = re.compile(value_re)
        string_re = '([a-zA-Z0-9_]*)'
        string_re_c = re.compile(string_re)
        self.defines = {}

        file = open(filename, "r")
        for line in file:
            if line.find("//") >= 0:
                continue
            if line.find("#define") >= 0:
                if line.find("#define TRICKLE_SIM_H") >= 0:
                    continue
                else:
                    define_obj = define_re_c.search(line)
                    if define_obj != None:
                        variable = define_obj.group(1)
                        value = define_obj.group(2)

                        try:
                            ivalue = int(value)
                        except:
                            value_obj = value_re_c.search(value)
                            if value_obj != None:
                                ivalue = int(value_obj.group(1))
                            else:
                                string_obj = string_re_c.search(value)
                                if string_obj != None:
                                    value = string_obj.group(1)
                                else:
                                    print "Could not parse value:", line

                        self.defines[variable] = ivalue
                    else:
                        print "Could not parse define:", line
        file.close()
        #print "Defines", self.defines

    def __str__(self):
        return "="*40 + "\n" \
            + str(self.defines) \
            + "\n" + "="*40
