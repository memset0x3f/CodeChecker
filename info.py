VERSION = 'v1.0'
AUTHOR = 'Fighter'
ABOUT = f"Version: {VERSION}\n\n" + "Code Checker: 一个支持多文件对拍的工具\n\n" + f"作者：Fighter"

FILE_ERR = "不支持的数据文件格式"
REPEAT_FILE = "当前文件已经在列表中，不可重复添加"
def RE(status):
	return f"运行数据生成器时遇到错误, 返回代码{status}\n请检查编译器或解释器是否正确安装，选择的文件是否存在，以及代码是否能正常运行"