import re
import os
import signal


def create_unique_file_name(name):
    """Create a unique file_name"""
    leading_zeros = 4
    file_name, file_extension = os.path.splitext(name)
    file_path, file_name = os.path.split(file_name)

    # check if file_name contains the number part and if so ignores it to
    # generate the next part
    expression = r"_\d{" + str(leading_zeros) + "}"
    file_name = re.sub(expression, "", file_name, count=1)
    file_name = os.path.join(file_path, file_name)

    new_name = ""
    cont = 0
    while True:
        cont += 1
        new_name = file_name + str(cont).zfill(leading_zeros) + file_extension
        if os.path.isfile(new_name):
            continue
        else:
            break

    unique_name = new_name.split("/")[-1]
    return os.path.join(file_path, unique_name)


if __name__ == "__main__":
    print(create_unique_file_name("daf_scan.nxs"))
    print(create_unique_file_name("adasdas/asdasdas/daf_scan.nxs"))
