# 其他解题器
* Python
  * 这两个用的栈短，分数远低于最优解。
  * https://github.com/svajoklis-1/mobius-front-solitaire-solver (e1)
  * https://github.com/jordan9001/mobius_solitaire_player (e2)
* C++
  * https://github.com/jonathanpaulson/mobiusfront_cribbage (还没看)
  * https://github.com/gregbartell/mf83_solitaire_solver (+Python 还没看)
* Jave
  * https://github.com/cmears/solitaire-cribbage (还没看)
* C#
  * https://github.com/madbarron/cribbage-solitaire-solver[ ]()(还没看)
# 其他关于MF83的仓库
* https://github.com/CahootsMalone/mobius-front-83-stuff
* https://github.com/leghort/Traduction-Mobius-Front-83
# v1 状况
* 代码和文件夹的`123456789ABCD`表示`A234567890JQK`(0=10)。  
* 记录10万个状态能在50秒左右求出足够好的解。记录1万个状态可以更快。
* 求最优解需要大约10G内存。
* 最快的题 #29 ~160s
  * ['B6B672582883A', '4C55767DD9611', '2443A2C1DA19C', 'C4B3BD78959A3']
* 最慢的题 #30 ~630s
  * ['A211753D89C78', '44D5B359AAC4B', '6387656B4C16D', '22A9132D98B7C']
* [早期版本录像1](https://www.bilibili.com/video/BV1QL411j7t4)
* [早期版本录像2](https://www.bilibili.com/video/BV1hm4y1X7LH)
# v2 状况
自用笔记本，CPU性能模式，CPU数量的进程，开着炉石，PyCharm中运行，`Deal #1`完全解。
  1. 限10万状态，66秒。（炉石占用8-30%的CPU）
  2. 标准情况，447秒。
  3. `pool.map`取代`pool.apply_async`，385秒，少15%的耗时。
  4. 4进程，431秒。
  5. 状态容器用`deque`，398秒。虽然append提高了，但extend，list()和sorted更耗时。
  6. 状态用`tuple`，203秒。wait时间大幅降低，score和sort快25%，lambda快33%，sorted快50%，列表复制的时间也省了，内存也省了。
  7. `list(chain(*lists))`取代`extend`，204秒。不用cProfile175秒。关炉石，CPU狂飙模式，152秒。关PyCharm用命令行142秒。用条件赋值取代字典，147秒。
* 优化点
  * `pool.map`取代`pool.apply_async`。
  * `tuple`取代`list`。
  * 条件赋值取代字典，不明显。
  * JIT？（试用numba时报错没调通）
  * 其他？
# v3 状况
只是清理。