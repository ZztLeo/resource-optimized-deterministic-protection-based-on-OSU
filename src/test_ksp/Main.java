package test_ksp;

import test_ksp.GraphEntity.*;

public class Main {
    public static void main(String[] args) {
        int n=6,e=9;

        //9行三列数组，每一列分别为开始点、终止点、该边权值
        int data[][]={{0,1,3},{0,2,2},{1,3,4},{2,1,1},{2,3,2},{2,4,3},{3,4,2},{3,5,1},{4,5,2}};

        MyGraph g=new MyGraph(n,e);
        g.createMyGraph(g,n,e,data);
        System.out.println("DFS遍历图的结果:");
        g.DFS(g,0);//从0开始遍历


        //调用ksp并打印最终结果
        ShortestPath ksp=new ShortestPath();
        System.out.println(ksp.KSP_Yen(g,0,5,6));
    }

}