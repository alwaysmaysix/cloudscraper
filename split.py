import sys
import os

def split_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    total_lines = len(lines)
    quarter = total_lines // 4

    for i in range(1, 4):
        new_filename = '{}.txt'.format(i)
        counter = 1
        while os.path.isfile(new_filename):
            new_filename = '{}({}).txt'.format(i, counter)
            counter += 1

        with open(new_filename, 'w') as file:
            for line in lines[i*quarter:(i+1)*quarter]:
                file.write(line)

    # Overwrite the original file with the first quarter
    with open(filename, 'w') as file:
        for line in lines[:quarter]:
            file.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_file.py <filename>")
    else:
        split_file(sys.argv[1])
