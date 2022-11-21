# Code Checker：基于PyQt的简单对拍工具

每次一份代码都要写一个对拍脚本，有时还要在不同的输入输出文件之间切换，实在是令人厌烦。

而Code Checker 旨在尝试让我们获得更轻松的对拍体验。在Code Checker 中

- 对拍和数据生成代码不需要包含输入输出重定向(如`c++`中的`freopen`， 添加重定向会导致Code Checker无法捕获输出)

- 通过可视化的文件选择，可以轻松的将不在同一目录下的文件一起对拍。

- 同时支持多个数据生成文件，依次对每一个数据生成器进行对拍。
- 同时支持多个对拍代码文件，不仅仅是两份代码之间的检查。
- 自定义对拍数据次数(0-1000)。

软件基于PyQt，开发环境为Manjaro Linux(主要) 和 Windows11(测试和修改)，现阶段仅经过了简单的测试，仍可能存在plenty of bugs.