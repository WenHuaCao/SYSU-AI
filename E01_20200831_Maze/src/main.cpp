#include <cstdio>
#include <fstream>
#include <queue>
#include <stack>
using namespace std;

constexpr int row = 18;
constexpr int col = 36;
constexpr int dir[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
typedef struct Node
{
    int x, y;
}Node;
int maze[row][col];
int vis[row][col];
Node pre[row][col];
Node startn, endn;

void bfs()
{
    queue<Node> q;
    q.push(startn);
    vis[startn.x][startn.y] = 1;
    while (1)
    {
        if (q.empty()) break;
        Node tmpn = q.front();
        q.pop();
        for (int i = 0; i < 4; i++)
        {
            Node next = {tmpn.x + dir[i][0], tmpn.y + dir[i][1]};
            if (!vis[next.x][next.y] && next.x >= 0 && next.x < row && next.y >= 0 && next.y < col && !maze[next.x][next.y])
            {
                pre[next.x][next.y] = tmpn;
                vis[next.x][next.y] = 1;
                q.push(next);
            }
        }
    }
}

void print(Node node)
{
    stack<Node> s;
    int x = node.x;
    int y = node.y;
    while (!(pre[x][y].x == 0 && pre[x][y].y == 0))
    {
        s.push(node);
        node = pre[x][y];
        x = node.x;
        y = node.y;
    }
    int len = s.size();
    while (!s.empty())
    {
        Node tmpn = s.top();
        s.pop();
        printf("(%d, %d) ", tmpn.x, tmpn.y);
    }
    printf("\nshortest path length: %d\n", len);
}

int main()
{
    ifstream fin("MazeData.txt");
    for (int i = 0; i < row; i++)
        for (int j = 0; j < col; j++)
        {
            char tmp;
            while (1)
            {
                fin >> tmp;
                if (tmp != '0' && tmp != '1' && tmp != 'S' && tmp != 'E') continue;
                else break;
            }
            if (tmp == 'S')
            {
                startn.x = i;
                startn.y = j;
                maze[i][j] = 1;
            }
            else if (tmp == 'E')
            {
                endn.x = i;
                endn.y = j;
                maze[i][j] = 0;
            }
            else
            {
                maze[i][j] = tmp - '0';
            }
        }
    fin.close();

    bfs();
    // for (int i = 0; i < row; i++)
    //     for (int j = 0; j < col; j++)
    //         printf("(%d, %d)\n", pre[i][j].x, pre[i][j].y);
    print(endn);
    return 0;
}