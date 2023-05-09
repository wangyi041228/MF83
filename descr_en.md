# Solvers
* Python
  * The stacks used by these two are small, and the scores are much lower than the optimal solution.
  * https://github.com/svajoklis-1/mobius-front-solitaire-solver (e1)
  * https://github.com/jordan9001/mobius_solitaire_player (e2)
* C++
  * https://github.com/jonathanpaulson/mobiusfront_cribbage (Not check)
  * https://github.com/gregbartell/mf83_solitaire_solver (+Python Not check)
* Jave
  * https://github.com/cmears/solitaire-cribbage (Not check)
* C#
  * https://github.com/madbarron/cribbage-solitaire-solver (Not check)
# Others about MF83
* https://github.com/CahootsMalone/mobius-front-83-stuff
* https://github.com/leghort/Traduction-Mobius-Front-83
# v1 info
* `123456789ABCD` in code/folder mean `A234567890JQK`(0=10).  
* It takes ~50 seconds to work out a good enough answer by keeping the best 100k states. Keep 10k states for higher speed.
* It takes ~10 G memory to work out the optimal score.
* Fastest Deal #29 ~160s
  * ['B6B672582883A', '4C55767DD9611', '2443A2C1DA19C', 'C4B3BD78959A3']
* Slowest Deal #30 ~630s
  * ['A211753D89C78', '44D5B359AAC4B', '6387656B4C16D', '22A9132D98B7C']
* [Early Record 1](https://www.bilibili.com/video/BV1QL411j7t4)
* [Early Record 2](https://www.bilibili.com/video/BV1hm4y1X7LH)
# v2 info
自用笔记本，CPU性能模式，CPU数量的进程，开着炉石，PyCharm中运行，`Deal #1`完全解。
  1. 限10万状态，66秒。（炉石占用8-30%的CPU）
  2. 标准情况，447秒。
  3. `pool.map`取代`pool.apply_async`，385秒，少15%的耗时。
  4. 4进程，431秒。
  5. 状态容器用`deque`，398秒。虽然append提高了，但extend，list()和sorted更耗时。
  6. 状态用`tuple`，203秒。wait时间大幅降低，score和sort快25%，lambda快33%，sorted快50%，列表复制的时间也省了，内存也省了。
  7. `list(chain(*lists))`取代`extend`，204秒。不用cProfile175秒。关炉石，CPU狂飙模式，152秒。关PyCharm用命令行142秒。
* 优化点
  * `pool.map`取代`pool.apply_async`。
  * `tuple`取代`list`。
  * JIT？（试用numba时报错没调通）
  * 其他？
# v3 info
Just a cleanup.