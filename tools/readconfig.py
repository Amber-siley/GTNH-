file = input("file_path: ")
with open(file,mode="r") as fp:
    content = repr(fp.read())[1:-1]
with open("value.txt",mode="w+") as fp:
    fp.write(content)