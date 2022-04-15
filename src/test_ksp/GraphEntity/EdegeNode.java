package test_ksp.GraphEntity;

public class EdegeNode{   //边表结点类
    public int adjvex;//边指向的点
    public int value;//边权值
    public EdegeNode nextEdge;
    public EdegeNode() {}
    public EdegeNode(int adjvex,int value)   //初始化边结点
    {
        this.adjvex=adjvex;
        this.value=value;
        this.nextEdge=null;
    }
}