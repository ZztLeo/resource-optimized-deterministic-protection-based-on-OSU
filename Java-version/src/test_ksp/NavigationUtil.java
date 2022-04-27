package test_ksp;

import test_ksp.GraphEntity.*;
public class NavigationUtil {
    /**
     * 获取两点之间权值
     * @param graph
     * @param i
     * @param j
     * @return
     */
    public static double getEdgeWight(MyGraph graph, int i, int j)
    {
        double w=0; 
        EdegeNode a = null;
        a=graph.point[i].firstArc;
        while(a!=null)
        {
            if(a.adjvex==j)
            {
                return w+a.value;
            }
            a=a.nextEdge;                                                    //实际上像是一种遍历链表的行为
        }
        return -1;
    }


    /**
     * 判断两点是否连通
     * @param graph
     * @param i
     * @param j
     * @return
     */
    public static boolean isConnected(MyGraph graph,int i,int j)
    {
        double w=0;
        EdegeNode a = null;
        a=graph.point[i].firstArc;
        while(a!=null)
        {
            if(a.adjvex==j)
            {
                return true;
            }
            a=a.nextEdge;                                                    //实际上像是一种遍历链表的行为
        }
        return false;
    }
}