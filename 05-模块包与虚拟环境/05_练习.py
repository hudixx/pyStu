import my_util
from my_util import repeat as rpt



def main() -> None:
    # 第1题
    print(rpt("go"))
    print(my_util.repeat("go", 3))
    #第2题
        #python my_util.py 打印： my_util.__name__ =  __main__
        #python 05_练习.py 打印： my_util.__name__ =  my_util
    # 第3题
        #python的venv，对应java里面的Maven/jdk时要解决的： 每个项目一份独立的jdk+本地仓库
    # 第4题
        # 打印： E:\myGitRepositorysx\pyStu\.venv\Scripts\python.exe

if __name__ == "__main__":
    main()