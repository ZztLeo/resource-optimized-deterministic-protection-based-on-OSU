package test_ksp;
import test_ksp.GraphEntity.*;
import java.util.*;

/**
 * <pre>
 *     author : 闻小玖
 *     time   : 2020/08/30
 *     desc   : 图的k最短路径
 *     version: 1.0
 * </pre>
 */
public class ShortestPath {

    public static class MyPath {
        // 路径上的各个节点对应的数组下标（从起点到终点）
        public List < Integer > path;
        // 路径总权值
        public double weight;
        // 路径上节点个数：通过path.size()得到


        public MyPath() {}

        public MyPath(List < Integer > path, double weight) {
            this.path = path;
            this.weight = weight;
        }

        @Override
        public String toString() {
            return "MyPath{" +
                    "path=" + path +
                    ", weight=" + weight +
                    '}';
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;

            MyPath path1 = (MyPath) o;
            return path != null ? path.equals(path1.path) : path1.path == null;
        }

        @Override
        public int hashCode() {
            int result;
            long temp;
            result = path != null ? path.hashCode() : 0;
            temp = Double.doubleToLongBits(weight);
            result = 31 * result + (int)(temp ^ (temp >>> 32));
            return result;
        }
    }


    /**
     * 用Yen's KSP算法从图中找出从startIndex到endIndex的K条最短路径
     *
     * @param g
     * @param startIndex:起始节点的数组下标
     * @param endIndex：终止节点的数组下标
     * @param K：要求的最短路径数目
     * @return
     */
    public List < MyPath > KSP_Yen(MyGraph g, int startIndex, int endIndex, int K) {
        // 结果列表
        List < MyPath > result = new ArrayList < > ();
        // 候选路径列表
        Set < MyPath > candidatePaths = new HashSet < > ();
        // 候选路径列表中权值最小的路径，及其对应的节点个数
        // 第一条最短路径
        MyPath p1 = getSingleShortestPath_dijkstra(g, startIndex, endIndex, null, null);
        result.add(p1);
        int k = 1;
        List < Integer > pk = p1.path;
        while (k < K) {
            /*
            求第k+1条最短路径
             */
            // 遍历每一个偏离点
            for (int i = 0; i <= pk.size() - 2; i++) {
                // 1，pk路径中起点到偏离点Vi的路径权值
                double w1 = 0;
                for (int j = 0; j <= i - 1; j++) {
                    w1 += NavigationUtil.getEdgeWight(g, pk.get(j), pk.get(j + 1));
                }
                // 2,偏离点到终点的最短路径
                MyPath viToDestinationSP = getSingleShortestPath_dijkstra(g,
                        pk.get(i), endIndex, pk.subList(0, i), result);
                if (viToDestinationSP != null) {
                    // 说明从这个偏离点可以到达终点
                    MyPath temp = new MyPath();
                    List < Integer > tempPath = new ArrayList < > (pk.subList(0, i));
                    tempPath.addAll(viToDestinationSP.path);
                    temp.path = tempPath;
                    temp.weight = w1 + viToDestinationSP.weight;
                    // 加入候选列表
                    if (!candidatePaths.contains(temp)) {
                        candidatePaths.add(temp);
                    }
                }
            }
            if (candidatePaths == null || candidatePaths.size() == 0) {
                // 没有候选路径，则无需再继续向下求解
                break;
            } else {
                // 从候选路径中选出最合适的一条，移除并加入到结果列表
                MyPath fitPath = getFitPathFromCandidate(candidatePaths);
                candidatePaths.remove(fitPath);
                result.add(fitPath);
                k++;
                pk = fitPath.path;
            }
        }
        return result;
    }
 
    /**
     * 从候选列表中得到一条路径作为pk+1
     * 要求：1）该路径的权值和最小；2）路径经过节点数最少
     * @param candidatePaths：候选列表
     * @return
     */
    private MyPath getFitPathFromCandidate(Set < MyPath > candidatePaths) {
        MyPath result = new MyPath(null, Double.MAX_VALUE);
        for (MyPath p: candidatePaths) {
            // 对于每一条路径
            if (p.weight < result.weight) {
                result = p;
            }
            if (p.weight == result.weight && p.path.size() < result.path.size()) {
                result = p;
            }
        }
        return result;
    }

    /**
     * 用Dijkstra算法得到从startIndex到endIndex的一条最短路径
     *
     * @param g
     * @param startIndex                               起始节点的数组下标
     * @param endIndex                                 终止节点的数组下标
     * @param unavailableNodeIndexs：求最短路径时不可用的节点（数组下标）
     * @param unavailableEdges：求最短路径时不可用的边
     * @return
     */
    public MyPath getSingleShortestPath_dijkstra(MyGraph g, int startIndex, int endIndex, List < Integer > unavailableNodeIndexs, List < MyPath > unavailableEdges) {
        if (startIndex == -1) {
            //            throw new Exception("getSingleShortestPath_dijkstra()起始点编号输入错误");
        }
        if (endIndex == -1) {
            //            throw new Exception("getSingleShortestPath_dijkstra()终止点编号输入错误");
        }
        int[] set = new int[g.numPoint]; // 是否已并入集合，该点是否已找到最短路径
        // s到i的最短路径长度
        double[] dist = new double[g.numPoint];
        // s到i的最短路径上i的前一个节点编号
        int[] path = new int[g.numPoint];

        // 初始化数组
        set[startIndex] = 1;
        for (int i = 0; i < g.numPoint; i++) {
            if (i == startIndex) { // 源点
                dist[i] = 0;
                path[i] = -1;
            } else {
                if (NavigationUtil.isConnected(g, startIndex, i)) {
                    dist[i] = NavigationUtil.getEdgeWight(g, startIndex, i);
                    path[i] = startIndex;
                } else {
                    dist[i] = Double.MAX_VALUE;
                    path[i] = -1;
                }
            }
        }

        // 不能走的边
        if (unavailableEdges != null && unavailableEdges.size() != 0) {
            for (MyPath p: unavailableEdges) {
                int index = p.path.indexOf(startIndex);
                if (index >= 0 && (index + 1) >= 0) {
                    dist[p.path.get(index + 1)] = Double.MAX_VALUE;
                    path[p.path.get(index + 1)] = -1;
                }
            }
        }

        // 不能走的点
        if (unavailableNodeIndexs != null && unavailableNodeIndexs.size() != 0) {
            for (Integer point: unavailableNodeIndexs) {
                set[point] = 1;
            }
        }

        // 需进行n-2轮循环
        for (int i = 0; i < g.numPoint - 2; i++) {
            int k = -1;
            double min = Double.MAX_VALUE;
            // 找出dist[]中最小的（太贪心了）
            for (int j = 0; j < g.numPoint; j++) {
                if (set[j] == 1) {
                    continue;
                }
                if (dist[j] < min) {
                    min = dist[j];
                    k = j;
                }
            }
            if (k == -1) {
                // 说明从源点出发与其余节点不连通，无法再向下进行扩展
                break;
            }
            set[k] = 1; // 把节点k并入
            // 修改dist[]、path[]
            for (int j = 0; j < g.numPoint; j++) {
                if (set[j] == 1) {
                    continue;
                }
                if (NavigationUtil.isConnected(g, k, j)) {
                    double temp = dist[k] + NavigationUtil.getEdgeWight(g, k, j);
                    if (temp < dist[j]) {
                        dist[j] = temp;
                        path[j] = k;
                    }
                }
            }
        }

        System.out.println("运行Dijkstra算法后的数组情况为：");
        System.out.print("set[]:");
        for (int i = 0; i < g.numPoint; i++) {
            System.out.print(set[i] + "\t");
        }
        System.out.println();
        System.out.print("dist[]:");
        for (int i = 0; i < g.numPoint; i++) {
            System.out.print(dist[i] + "\t");
        }
        System.out.println();
        System.out.print("path[]:");
        for (int i = 0; i < g.numPoint; i++) {
            System.out.print(path[i] + "\t");
        }
        System.out.println();
        // 输出
        if (dist[endIndex] == Double.MAX_VALUE) {
            // 说明没有最短路径，两点不连通
            System.out.println("两点之间不连通");
            return null;
        } else {
            System.out.println("节点" + g.point[startIndex].data+ "到节点" +
                    g.point[endIndex].data + "的最短路径长度为：" + dist[endIndex] + "，具体路径是：");
            MyPath result = new MyPath();
            result.path = getMinimumPath(g, startIndex, endIndex, path);
            result.weight = dist[endIndex];
            return result;
        }
    }

    /**
     * 输出从节点S到节点T的最短路径
     *
     * @param sIndex：起始节点在数组中下标
     * @param tIndex：终止节点在数组中下标
     */
    private List < Integer > getMinimumPath(MyGraph g, int sIndex, int tIndex, int[] path) {
        List < Integer > result = new ArrayList < > ();
        Stack < Integer > stack = new Stack < > ();
        stack.push(tIndex);
        int i = path[tIndex];
        while (i != -1) {
            stack.push(i);
            i = path[i];
        }
        while (!stack.isEmpty()) {
            System.out.print(g.point[stack.peek()].data + ":" + g.point[stack.peek()].data + "-->");
            result.add(g.point[stack.pop()].data);
        }
        System.out.println();
        return result;
    }

}
