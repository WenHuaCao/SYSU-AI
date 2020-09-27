#include <iostream>
#include <cstdio>
#include <algorithm>
#include <stack>
#include <vector>
using namespace std;

constexpr int N = 4;
constexpr int dir[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
int puzzle[N][N];
int next_limit = 0x7f7f7f7f;
int cnt = 0;

typedef struct Node
{
    int p[N][N];        // puzzle当前状态
    int x, y;           // 数码“0”的横纵坐标
    vector<int> path;   // 记录初始状态到当前状态的数码移动顺序
}Node;

bool valid()
{
    // 计算初始状态逆序数
    int reverse = 0;
    int v[N * N - 1];
    int pos = 0;
    int x;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
        {
            if (puzzle[i][j] == 0)
            {
                x = i;
                continue;
            }
            else v[pos++] = puzzle[i][j];
        }
    for (int i = 0; i < N * N - 1; i++)
        for (int j = 0; j < i; j++)
            if (v[j] > v[i]) reverse++;
    
    // N为偶数时，先计算出从初始状态到指定状态，空位要移动的行数m，
    // 如果初始状态的逆序数加上m与指定状态的逆序数奇偶性相同，则有解;
    // N为奇数时，初始状态与指定状态逆序数奇偶性相同即有解
    if (N % 2 == 0)
    {
        int res = reverse + N - 1 - x;
        if (res % 2 == 0) return true;
        else return false;
    }
    else
    {
        if (reverse % 2 == 0) return true;
        else return false;
    }
}

int h(int p[N][N])
{
    int dism = 0;

    // 计算曼哈顿距离
    for (int i = 0; i < N; i++)
        for (int j = 1; j <= N; j++)
        {
            if (p[i][j - 1] == 0) continue;
            else if (p[i][j - 1] != i * N + j)
            {
                int x = (p[i][j - 1] - 1) / N;
                int y = p[i][j - 1] - x * N;
                dism += abs(i - x) + abs(j - y);
            }
        }
    return dism;
}

bool is_goal(int p[N][N])
{
    // 判定当前是否已经到达目标状态
    for (int i = 0; i < N; i++)
        for (int j = 1; j <= N; j++)
        {
            if (p[i][j - 1] == 0)
            {
                if (i != N - 1 && j != N) return false;
            }
            else
            {
                if (p[i][j - 1] != i * N + j) return false;
            }   
        }
    return true;
}

void print(Node n)
{
    // 打印结果
    int len = n.path.size();
    printf("%d steps finished\n", cnt);
    printf("%d moves required\n", len);
    for (int i = 1; i <= len; i++)
    {
        printf("%4d", n.path[i - 1]);
        if (i % 10 == 0) printf("\n");
    }
}

bool dfs(int limit, Node tmpn)
{
    // 函数调用计数
    cnt++;

    // 判定是否到达最终状态
    if (is_goal(tmpn.p))
    {
        print(tmpn);
        return true;
    }

    // 四个方向依次循环
    for (int i = 0; i < 4; i++)
    {
        int dx = dir[i][0];
        int dy = dir[i][1];
        int x = tmpn.x + dx;
        int y = tmpn.y + dy;

        // 判定目标位置是否合法
        if (x >= 0 && x < N && y >= 0 && y < N)
        {
            // 不能往回走
            if (tmpn.path.size() != 0 && \
                tmpn.path[tmpn.path.size() - 1] == tmpn.p[x][y])
                continue;
            
            // 下一步
            int tmpx = tmpn.x;
            int tmpy = tmpn.y;
            tmpn.p[tmpn.x][tmpn.y] = tmpn.p[x][y];
            tmpn.p[x][y] = 0;
            tmpn.path.push_back(tmpn.p[tmpn.x][tmpn.y]);
            tmpn.x = x;
            tmpn.y = y;

            // 判定边界
            int f = h(tmpn.p) + tmpn.path.size();
            if (f <= limit)
            {
                if (dfs(limit, tmpn)) return true;
            }
            else
            {
                if (f < next_limit) next_limit = f;
            }
            
            // 回溯
            tmpn.x = tmpx;
            tmpn.y = tmpy;
            tmpn.path.pop_back();
            tmpn.p[x][y] = tmpn.p[tmpn.x][tmpn.y];
            tmpn.p[tmpn.x][tmpn.y] = 0;
        }
    }

    // 搜索失败
    return false;
}

int main()
{
    int zx, zy;
    // 输入puzzle
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
        {
            cin >> puzzle[i][j];
            if (puzzle[i][j] == 0)
            {
                zx = i;
                zy = j;
            }
        }

    // 判定是否有解
    bool v = valid();
    if (!v)
    {
        cout << "Impossible!" << endl;
        return 0;
    }

    // 定义起始节点和深度
    Node start;
    int limit = h(puzzle);
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            start.p[i][j] = puzzle[i][j];
    start.path = {};
    start.x = zx;
    start.y = zy;

    while (true)
    {
        if (dfs(limit, start)) break;
        limit = next_limit;
        next_limit = 0x7f7f7f7f;
    }

    return 0;
}