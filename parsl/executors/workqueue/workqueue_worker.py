import sys
import pickle
import logging
from ipyparallel.serialize import unpack_apply_message, serialize_object


def check_file(parsl_file_obj, mapping, file_type_string):
    type_desc = type(parsl_file_obj)
    if file_type_string is None:
        file_type_string = "<class 'parsl.data_provider.files.File'>"
    if type_desc == file_type_string:
        if parsl_file_obj.filepath in mapping:
            parsl_file_obj.local_path = mapping[parsl_file_obj.filepath]


if __name__ == "__main__":
    name = "parsl"
    logger = logging.getLogger(name)

    shared_fs = False
    input_function_file = ""
    output_result_file = ""
    remapping_string = None
    file_type_string = None

    try:
        index = 1
        while index < len(sys.argv):
            if sys.argv[index] == "-i":
                input_function_file = sys.argv[index + 1]
                index += 1
            elif sys.argv[index] == "-o":
                output_result_file = sys.argv[index + 1]
                index += 1
            elif sys.argv[index] == "-r":
                remapping_string = sys.argv[index + 1]
                index += 1
            elif sys.argv[index] == "-t":
                file_type_string = sys.argv[index + 1]
                index += 1
            elif sys.argv[index] == "--shared-fs":
                shared_fs = True
            else:
                print("command line argument not supported")
                exit(1)
            index += 1
    except Exception as e:
        print(e)
        exit(1)

    try:
        input_function = open(input_function_file, "rb")
        function_tuple = pickle.load(input_function)
        input_function.close()
    except Exception:
        exit(2)

    user_ns = locals()
    user_ns.update({'__builtins__': __builtins__})
    f, args, kwargs = unpack_apply_message(function_tuple, user_ns, copy=False)

    mapping = {}

    try:
        if shared_fs is False and remapping_string is not None:

            for i in remapping_string.split(","):
                split_mapping = i.split(":")
                mapping[split_mapping[0]] = split_mapping[1]

            func_inputs = kwargs.get("inputs", [])
            for inp in func_inputs:
                check_file(inp, mapping, file_type_string)

            for kwarg, potential_f in kwargs.items():
                check_file(potential_f, mapping, file_type_string)

            for inp in args:
                check_file(inp, mapping, file_type_string)

            func_outputs = kwargs.get("outputs", [])
            for output in func_outputs:
                check_file(output, mapping, file_type_string)
    except Exception:
        exit(3)

    prefix = "parsl_"
    fname = prefix + "f"
    argname = prefix + "args"
    kwargname = prefix + "kwargs"
    resultname = prefix + "result"

    user_ns.update({fname: f,
                    argname: args,
                    kwargname: kwargs,
                    resultname: resultname})

    code = "{0} = {1}(*{2}, **{3})".format(resultname, fname,
                                           argname, kwargname)

    try:
        # logger.debug("[RUNNER] Executing: {0}".format(code))
        exec(code, user_ns, user_ns)
    except Exception:
        exec_info = sys.exc_info()
        result_package = {"failure": True, "result": serialize_object(exec_info)}
    else:
        result = user_ns.get(resultname)
        result_package = {"failure": False, "result": serialize_object(result)}
    try:
        f = open(output_result_file, "wb")
        pickle.dump(result_package, f)
        f.close()
        exit(0)
    except Exception:
        exit(4)
